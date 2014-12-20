#pragma once

#include <Eigen/Dense>
#include <iostream>
#include <vector>

#include <boost/random/mersenne_twister.hpp>
#include <boost/shared_ptr.hpp>

#include "sphere.hpp"
#include "dpmeans.hpp"
#include "dir.hpp"
#include "cat.hpp"

using namespace Eigen;
using std::cout;
using std::endl;

#ifdef BOOST_OLD
#define mt19937 boost::mt19937
#else
using boost::mt19937;
#endif

#define UNASSIGNED 4294967295

template<class T, class DS>
class DDPMeans : public DPMeans<T,DS>
{
public:
  DDPMeans(const shared_ptr<Matrix<T,Dynamic,Dynamic> >& spx,
      T lambda, T Q, T tau, mt19937* pRndGen);
  DDPMeans(const shared_ptr<ClData<T> >& cld,
      T lambda, T Q, T tau, mt19937* pRndGen);
  virtual ~DDPMeans();

//  void initialize(const Matrix<T,Dynamic,Dynamic>& x);
  virtual void updateLabelsSerial();
  virtual void updateLabels();
  virtual void updateCenters();
  
  virtual void nextTimeStep(const shared_ptr<Matrix<T,Dynamic,Dynamic> >& spx);
  virtual void nextTimeStep(const shared_ptr<ClData<T> >& cld);
  virtual void updateState(); // after converging for a single time instant

  virtual uint32_t indOfClosestCluster(int32_t i, T& sim_closest);

  virtual bool converged(T eps=1e-6) 
  {
    return this->counts().size() > 0 && this->counts().size() == prevNs_.size()
      && (prevNs_.array() == this->counts().array()).all();
  };

  VectorXf ages(){
    VectorXf ts(this->K_);
    for(uint32_t k=0; k<this->K_; ++k) ts(k) = this->cls_[k]->t();
    return ts;
  };

  VectorXf weights(){
    VectorXf ws(this->K_);
    for(uint32_t k=0; k<this->K_; ++k) ws(k) = this->cls_[k]->w();
    return ws;
  };

protected:

  T Kprev_; // K before updateLabels()
  VectorXu prevNs_;
  uint32_t globalMaxInd_;

  typename DS::DependentCluster cl0_;
  vector< shared_ptr<typename DS::DependentCluster> > clsPrev_; // prev clusters 

  virtual uint32_t optimisticLabelsAssign(uint32_t i0);
};

// -------------------------------- impl ----------------------------------
template<class T, class DS>
DDPMeans<T,DS>::DDPMeans(const shared_ptr<Matrix<T,Dynamic,Dynamic> >& spx, 
    T lambda, T Q, T tau, mt19937* pRndGen)
  : DPMeans<T,DS>(spx,0,lambda,pRndGen), cl0_(tau,lambda,Q)
{
  this->Kprev_ = 0; // so that centers are initialized directly from sample mean
};

template<class T, class DS>
DDPMeans<T,DS>::DDPMeans(const shared_ptr<ClData<T> >& cld, 
    T lambda, T Q, T tau, mt19937* pRndGen)
  : DPMeans<T,DS>(cld,0,lambda,pRndGen), cl0_(tau,lambda,Q)
{
  this->Kprev_ = 0; // so that centers are initialized directly from sample mean
};

template<class T, class DS>
DDPMeans<T,DS>::~DDPMeans()
{}

template<class T, class DS>
uint32_t DDPMeans<T,DS>::indOfClosestCluster(int32_t i, T& sim_closest)
{
  int z_i = this->K_;
  sim_closest = this->lambda_;
  T sim_k = 0.;
  for (uint32_t k=0; k<this->K_; ++k)
  {
    sim_k = this->cls_[k]->dist(this->cld_->x()->col(i)); 
    if(DS::closer(sim_k, sim_closest))
    {
      sim_closest = sim_k;
      z_i = k;
    }
  }
  return z_i;
}

template<class T,class DS>
uint32_t DDPMeans<T,DS>::optimisticLabelsAssign(uint32_t i0)
{
  uint32_t idAction = UNASSIGNED;
#pragma omp parallel for 
  for(uint32_t i=i0; i<this->N_; ++i)
  {
    T sim = 0.;
    uint32_t z_i = indOfClosestCluster(i,sim);
    if(z_i == this->K_ || !this->cls_[z_i]->isInstantiated())
    { // note this as starting position
#pragma omp critical
      {
        if(idAction > i) idAction = i;
      }
    }
    this->cld_->z(i) = z_i;
  }
  return idAction;
};

template<class T, class DS>
void DDPMeans<T,DS>::updateLabels()
{
  uint32_t idAction = UNASSIGNED;
  uint32_t i0 = 0;
  do{
    idAction = optimisticLabelsAssign(i0);
    if(idAction != UNASSIGNED)
    {
      T sim = 0.;
      uint32_t z_i = this->indOfClosestCluster(idAction,sim);
      if(z_i == this->K_) 
      { // start a new cluster
        this->cls_.push_back(shared_ptr<typename DS::DependentCluster>(new
              typename DS::DependentCluster(this->cld_->x()->col(idAction),cl0_)));
        this->cls_[z_i]->globalId = this->globalMaxInd_++;
        this->K_ ++;
        cout<<"new cluster "<<(this->K_-1)<<endl;
      } 
      else if(!this->cls_[z_i]->isInstantiated())
      { // instantiated an old cluster
        this->cls_[z_i]->reInstantiate(this->cld_->x()->col(idAction));
        cout<<"revieve cluster "<<z_i<<endl;
      }
      i0 = idAction;
    }
    cout<<" K="<<this->K_<<" Ns="<<this->counts().transpose()<<endl;
  }while(idAction != UNASSIGNED);
  // if a cluster runs out of labels reset it to the previous mean!
  for(uint32_t k=0; k<this->K_; ++k)
    if(!this->cls_[k]->isInstantiated()) this->cls_[k] = this->clsPrev_[k];
};

template<class T, class DS>
void DDPMeans<T,DS>::updateLabelsSerial()
{
  //TODO this one may be broken by now
  for(uint32_t i=0; i<this->N_; ++i)
  {
    T sim = 0.;
    uint32_t z_i = indOfClosestCluster(i,sim);
    if(z_i == this->K_) 
    { // start a new cluster
      this->cls_.push_back(shared_ptr<typename DS::DependentCluster>(new
            typename DS::DependentCluster(this->cld_->x()->col(i),cl0_)));
      this->K_ ++;
    } else {
      if(!this->cls_[z_i]->isInstantiated())
      { // instantiated an old cluster
        this->cls_[z_i]->reInstantiate(this->cld_->x()->col(i));
      }
      ++ this->cls_[z_i]->N();
    }
    if(this->cld_->z(i) != UNASSIGNED) -- this->cls_[z_i]->N();
    this->cld_->z(i) = z_i;
  }
};

template<class T, class DS>
void DDPMeans<T,DS>::updateCenters()
{
  prevNs_.resize(this->K_);
  for(uint32_t k=0; k<this->K_; ++k)
    prevNs_(k) = this->cls_[k]->N();

  this->cld_->updateLabels(this->K_);
  this->cld_->computeSS();

//#pragma omp parallel for 
  for(uint32_t k=0; k<this->K_; ++k)
  {
    this->cls_[k]->updateSS(this->cld_,k);
    if(this->cls_[k]->isInstantiated()) 
    { // have data to update kth cluster
      if(k < this->Kprev_){
        this->cls_[k]->reInstantiate();
      }else{
        this->cls_[k]->updateCenter();
      }
    }
  }
};

template<class T, class DS>
void DDPMeans<T,DS>::nextTimeStep(const shared_ptr<Matrix<T,Dynamic,Dynamic> >& spx)
{
  return nextTimeStep(shared_ptr<ClData<T> >(new ClData<T>(spx,this->K_)));
};

template<class T, class DS>
void DDPMeans<T,DS>::nextTimeStep(const shared_ptr<ClData<T> >& cld)
{
  this->clsPrev_.clear();
  for (uint32_t k =0; k< this->K_; ++k)
  {
    clsPrev_.push_back(shared_ptr<typename
        DS::DependentCluster>(this->cls_[k]->clone())); 
    this->cls_[k]->N() = 0;
  }

  this->Kprev_ = this->K_;
//  assert(this->D_ == spx->rows());
//  if(this->spx_.get() != spx.get()) this->spx_ = spx; // update the data
  this->cld_ = cld;
  this->N_ = this->cld_->N();
//  this->z_.resize(this->N_);
//  this->z_.fill(UNASSIGNED);
};

template<class T, class DS>
void DDPMeans<T,DS>::updateState()
{
  vector<bool> toRemove(this->K_,false);
  for(uint32_t k=0; k<this->K_; ++k)
  {
    if(this->cls_[k]->isInstantiated()) this->cls_[k]->updateWeight();

    this->cls_[k]->incAge();

    if(this->cls_[k]->isDead()) toRemove[k] = true;

    this->cls_[k]->print();
  }

  vector<int32_t> labelMap(this->K_);
  for(int32_t k=0; k<this->K_; ++k)
    labelMap[k] = k;
  int32_t nRemoved = 0;
  for(int32_t k=this->K_; k>=0; --k)
    if(toRemove[k])
    {
      for(int32_t j=k; j<this->K_; ++j) -- labelMap[j];
      ++ nRemoved;
      this->cls_.erase(this->cls_.begin()+k);
    }
  this->K_ -= nRemoved;

  if(nRemoved > 0)
  {
    //TODO
    cout<<"labelMap: ";
    for(int32_t k=0; k<this->K_+nRemoved; ++k) cout<<labelMap[k]<<" ";
    cout<<endl;
    this->cld_->labelMap(labelMap);
  }
};

