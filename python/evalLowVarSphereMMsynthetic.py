import numpy as np
import subprocess as subp

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import mayavi.mlab as mlab

from matplotlib.patches import Ellipse

import ipdb, re
import os.path
import time, copy

from js.utils.plot.colors import colorScheme
from js.utils.config import Config2String

from vpCluster.manifold.karcherMean import karcherMeanSphere_propper
from vpCluster.manifold.sphere import Sphere

import matplotlib as mpl                                                        

#poster
mpl.rc('font',size=35) 
mpl.rc('lines',linewidth=4.)
figSize = (12, 14)

#paper
mpl.rc('font',size=40) 
mpl.rc('lines',linewidth=4.)
figSize = (14, 5.5)
figSize = (14, 12)
legendSize = 35

mpl.rc('figure', autolayout=True)


def mutualInfo(z,zGt):
  ''' assumes same number of clusters in gt and inferred labels '''
  N = float(z.size)
  Kgt = int(np.max(zGt)+1)
  K = int(np.max(z)+1)
  print Kgt, K
  mi = 0.0
  for j in range(K):
    for k in range(Kgt):
      Njk = float(np.logical_and(z==j,zGt==k).sum())
      Nj = float((z==j).sum())
      Nk = float((zGt==k).sum())
      if Njk > 0:
#        print '{} {} {} {} {} -> += {}'.format(N, Njk,Nj,Nk, N*Njk/(Nj*Nk), Njk/N * np.log(N*Njk/(Nj*Nk)))
        mi += Njk/N * np.log(N*Njk/(Nj*Nk))
  return mi
def entropy(z):
  ''' assumes same number of clusters in gt and inferred labels '''
  N = float(z.size)
  K = int(np.max(z)+1)
  H = 0.0
  for k in range(K):
    Nk = float((z==k).sum())
    if Nk > 0:
#        print '{} {} {} {} {} -> += {}'.format(N, Njk,Nj,Nk, N*Njk/(Nj*Nk), Njk/N * np.log(N*Njk/(Nj*Nk)))
      H -= Nk/N * np.log(Nk/N)
  return H

def run(cfg,reRun):
  params = np.array([cfg['lambda']])
  #args = ['../build/dpSubclusterSphereGMM',
#  args = ['../build/dpStickGMM',
  args = ['../build/dpMMlowVarCluster',
    '--seed {}'.format(int(time.time()*100000) - 100000*int(time.time())),
    '-N {}'.format(N), #TODO: read N,D from file!
    '-D {}'.format(D),
    '-K {}'.format(cfg['K']),
    '-T {}'.format(cfg['T']),
    #'--base NiwSphereUnifNoise',
    '--base '+cfg['base'],
    '-i {}'.format(cfg['rootPath']+cfg['dataPath']),
    '-o {}'.format(cfg['outName']+'.lbl'),
    '--shuffle',
    '--silhouette',
    '--params '+' '.join([str(p) for p in params])]

  if reRun:
    print ' '.join(args)
    print ' --------------------- '
    time.sleep(1)
    err = subp.call(' '.join(args),shell=True)
    if err:
      print 'error when executing'
      raw_input()
  z = np.loadtxt(cfg['outName']+'.lbl',dtype=int,delimiter=' ')
  sil = np.loadtxt(cfg['outName']+'.lbl_measures.csv',delimiter=" ")
  return z,sil

cfg = dict()
cfg['rootPath'] = rootPath = '../results/'
print cfg

dataPath = './rndSphereData.csv';
dataPath = './rndSphereDataIw.csv';
dataPath = './rndSphereDataElipticalCovs.csv';
dataPath = './rndSphereDataElipticalCovs1.csv';
dataPath = './rndSphereDataElipticalCovs2.csv'; # 10k datapoints with 30 classes
dataPath = './rndSphereDataElipticalCovs3.csv'; # 10k datapoints with 30 classes

# for final eval
dataPath = './rndSphereDataElipticalCovs4.csv'; # 10k datapoints with 30 classes less spread
dataPath = './rndSphereDataIwUncertain.csv';

# rebuttal
dataPath = './rndSphereDataNu9D20.csv';
dataPath = './rndSphereNu9D20N30000.csv';
dataPath = './rndSphereDataNu29D20N30000.csv';
dataPath = './rndSphereDataNu25D20N30000.csv';
dataPath = './rndSphereDataNu26D20N30000.csv';

dataPath = './rndSphereDataIwUncertain.csv'; # still works well in showing advantage of DpNiwSphereFull
dataPath = './rndSphereDataElipticalCovs4.csv'; # 10k datapoints with 30 classes less spread


# aistats resubmission
dataPath = './rndSphereDataIwUncertain.csv'; # still works well in showing advantage of DpNiwSphereFull
dataPath = './rndSphereDataNu25D3N30000NonOverLap.csv' # a few anisotropic clusters
dataPath = './rndSphereDataNu10D3N30000NonOverLap.csv' # very isotropic
dataPath = './rndSphereminAngle_15.0-K_30-N_30000-delta_4.0-nu_3.001-D_3.csv'
dataPath = './rndSphereminAngle_15.0-K_30-N_30000-delta_100.0-nu_21.0-D_20.csv'
dataPath = '././rndSphereminAngle_15.0-K_30-N_30000-delta_30.0-nu_21.0-D_20.csv'
dataPath = './rndSphereminAngle_15.0-K_30-N_30000-delta_30.0-nu_21.0-D_20.csv'
dataPath = './rndSphereminAngle_10.0-K_60-N_60000-delta_30.0-nu_21.0-D_20.csv'
dataPath = '././rndSphereminAngle_10.0-K_60-N_60000-delta_25.0-nu_21.0-D_20.csv'

# DP-vMF-means
dataPath = './rndSphereDataElipticalCovs4.csv'; # 10k datapoints with 30 classes less spread
dataPath = './rndSphereDataIwUncertain.csv';

cfg['dataPath'] = dataPath

if os.path.isfile(re.sub('.csv','_gt.lbl',rootPath+dataPath)):
  zGt = np.loadtxt(re.sub('.csv','_gt.lbl',rootPath+dataPath),dtype=int,delimiter=' ')
  Kgt = np.max(zGt)+1
else:
  print "groundtruth not found"

# aistats resubmission
bases = ['DPvMFmeans']
# params for the different al5os
bases = ['spkm','DPvMFmeans']
bases = ['spkm']
bases = ['DPvMFmeans','spkm']

cfg['nParms'] = 50;
paramBase = {'spkm':np.floor(np.linspace(70,10,cfg['nParms'])).astype(int), # 60,2
  'DPvMFmeans':np.array([ang for ang in np.linspace(10.,45.,cfg['nParms'])])}
paramName =  {'spkm':"$K$",'DPvMFmeans':"$\lambda$ [deg]"}
baseMap={'spkm':'spkm','kmeans':'k-means','NiwSphere':'DirSNIW', \
  'DpNiw':'DP-GMM','DpNiwSphere':'DpSNIW opt','DpNiwSphereFull':'DP-TGMM', \
  'DPvMFmeans':'DP-vMF-means'}

print paramBase

x=np.loadtxt(rootPath+dataPath,delimiter=' ')
N = x.shape[1]
D = x.shape[0]

reRun = True
reRun = False

cfg['T'] = 100
cfg['nRun'] =  10 #30

mis = {'spkm':np.zeros((len(paramBase['spkm']),cfg['nRun'])), 'DPvMFmeans':np.zeros((len(paramBase['DPvMFmeans']),cfg['nRun']))}
nmis = {'spkm':np.zeros((len(paramBase['spkm']),cfg['nRun'])), 'DPvMFmeans':np.zeros((len(paramBase['DPvMFmeans']),cfg['nRun']))}
vMeasures = {'spkm':np.zeros((len(paramBase['spkm']),cfg['nRun'])), 'DPvMFmeans':np.zeros((len(paramBase['DPvMFmeans']),cfg['nRun']))}
Ns = {'spkm':np.zeros((len(paramBase['spkm']),cfg['nRun'])), 'DPvMFmeans':np.zeros((len(paramBase['DPvMFmeans']),cfg['nRun']))}
Sils = {'spkm':np.zeros((len(paramBase['spkm']),cfg['nRun'])), 'DPvMFmeans':np.zeros((len(paramBase['DPvMFmeans']),cfg['nRun']))}

cfg0 = copy.deepcopy(cfg)
for i,base in enumerate(bases):
  cfg = copy.deepcopy(cfg0)
  cfg['base']=base
  cfg['outName'],_ = os.path.splitext(cfg['rootPath']+cfg['dataPath'])
  cfg['outName'] += '_'+Config2String(cfg).toString()
  print cfg['outName']
  if not reRun and os.path.exists('./'+cfg['outName']+'_MI.csv'):
    MI = np.loadtxt(cfg['outName']+'_MI.csv')
    Hgt = np.loadtxt(cfg['outName']+'_Hgt.csv')
    Hz = np.loadtxt(cfg['outName']+'_Hz.csv')
    Ns[base] = np.loadtxt(cfg['outName']+'_Ns.csv')
    Sils[base] = np.loadtxt(cfg['outName']+'_Sil.csv')
    print MI.shape, Hgt.shape, Hz.shape, Ns[base].shape
  else:
    MI = np.zeros((len(paramBase[base]),cfg['nRun']))
    Hz = np.zeros((len(paramBase[base]),cfg['nRun']))
    Hgt = np.zeros((len(paramBase[base]),cfg['nRun']))
    Sils[base] = np.zeros((len(paramBase[base]),cfg['nRun']))
    Ns[base] = np.zeros((len(paramBase[base]),cfg['nRun']))
    for j,param in enumerate(paramBase[cfg['base']]):
      if cfg['base'] == 'spkm':
        cfg['K'] = int(np.floor(param))
      else:
        cfg['K'] = 1
      if cfg['base'] == 'DPvMFmeans':
        cfg['lambda'] = np.cos(param*np.pi/180.0)-1. 
      else:
        cfg['lambda'] = 0.
      for t in range(cfg['nRun']):
        cfg['runId'] = t;
        z,measures = run(cfg,reRun)
        # compute MI and entropies - if not already computed and stored 
        Sils[base][j,t] = measures
        MI[j,t] = mutualInfo(z[-1,:],zGt)
        Hz[j,t] = entropy(z[-1,:])
        Hgt[j,t] = entropy(zGt)
        Ns[base][j,t] = int(np.max(z[-1,:])+1)
    np.savetxt(cfg['outName']+'_MI.csv',MI);
    np.savetxt(cfg['outName']+'_Hgt.csv',Hgt);
    np.savetxt(cfg['outName']+'_Hz.csv',Hz);
    np.savetxt(cfg['outName']+'_Sil.csv',Sils[base]);
    np.savetxt(cfg['outName']+'_Ns.csv',Ns[base]);

  mis[base] = MI
#  for t in range(cfg['T']):
#    for j in range(paramBase[base]):
  nmis[base] = MI / np.sqrt(Hz*Hgt)
  vMeasures[base] = 2.* MI / (Hz+Hgt)
  print mis[base].shape, nmis[base].shape, vMeasures[base].shape
#  print nmis[i,t], 2.*MI[t], Hz[t], Hgt[t]

print "done with the runs"

#cl = cm.gnuplot2(np.arange(len(bases)))
cl = cm.hsv(np.arange(255))
cl = cm.brg(np.arange(255))
cl = cm.gist_rainbow(np.arange(255))
cl = cm.gnuplot2(np.arange(255))
cl = cm.gnuplot(np.arange(255))
cl = cm.spectral(np.arange(255))
#print cltlib 
I = len(bases) +1

#fig = plt.figure(figsize=figSize, dpi=80, facecolor='w', edgecolor='k')
#for i,base in enumerate(bases):
#  plt.subplot(1,3,i+1)
#  plt.plot(paramBase[base],nmis[base][:,-1],label=baseMap[base],c=cl[(i+1)*255/I])
#  plt.title(base)
#  plt.xlabel(paramName[base])
#  plt.ylabel('NMI')
#  plt.ylim([0,1])
#  plt.legend(loc='lower right')
#plt.tight_layout()

#ipdb.set_trace()

indSpkm = np.ones(len(paramBase['spkm']),dtype=bool)
indSpkm[Ns['spkm'].mean(axis=1) < Ns['DPvMFmeans'].min()] = False
indSpkm[Ns['spkm'].mean(axis=1) > Ns['DPvMFmeans'].max()] = False

paramBase['spkm'] = paramBase['spkm'][indSpkm]
nmis['spkm'] = nmis['spkm'][indSpkm,:]
mis['spkm'] = mis['spkm'][indSpkm,:]
Ns['spkm'] = Ns['spkm'][indSpkm,:]
Sils['spkm'] = Sils['spkm'][indSpkm,:]

def plotOverParams(values,name,showLeg=None):
  colA = colorScheme('labelMap')['orange']
  colB = colorScheme('labelMap')['turquoise']

  fig = plt.figure(figsize=figSize, dpi=80, facecolor='w', edgecolor='k')
  ax1 = plt.subplot(111)
  base = 'spkm'
  Nmean = Ns[base].mean(axis=1)
  valMean = values[base].mean(axis=1)
  valStd = values[base].std(axis=1)
#  print name,base,valMean
#  print name,base,valStd
  leg1 = ax1.plot(valMean,paramBase[base],label=baseMap[base],c=colA)
  ax1.plot(valMean-valStd,paramBase[base],'--',label=baseMap[base],c=colA,lw=2,alpha=0.7)
  ax1.plot(valMean+valStd,paramBase[base],'--',label=baseMap[base],c=colA,lw=2,alpha=0.7)
  ax1.fill_betweenx(paramBase[base],valMean-valStd , valMean+valStd, color=colA, alpha=0.3)
  if name == '$K$':
    leg1 += ax1.plot([30]*len(paramBase[base]), paramBase[base], label="$K_{GT}=30$", c=colorScheme('labelMap')['red'])
  iKtrue = np.where(np.abs(Nmean-30)<2)
  if not name == '$K$':
    ax1.plot(values[base].mean(axis=1)[iKtrue],paramBase[base][iKtrue],'x',mew=4,ms=15,label=baseMap[base]+' $K={}$'.format(Nmean[iKtrue]),c=colorScheme('labelMap')['red'])
  ax1.set_ylabel(paramName[base],color=colA)  
  ax1.set_ylim(paramBase[base].min(),paramBase[base].max())
  ax1.invert_yaxis()
  for  tl in ax1.get_yticklabels():
    tl.set_color(colA)
  tiks = ax1.get_yticks()
  tikLbl = [str(tik) for tik in tiks[:-1]] 
  tikLbl += [''] 
  ax1.set_yticklabels(tikLbl)
#  ax1.legend(loc='best')
  ax1.set_xlabel(name)  
  if name == 'NMI':
    tiks = ax1.get_xticks()
    tikLbl = []
    for tik in tiks[::2]:
      tikLbl += [str(tik),'']
    del tikLbl[-1]
    ax1.set_xticklabels(tikLbl)

  ax2 = ax1.twinx()
  base = 'DPvMFmeans'
  Nmean = Ns[base].mean(axis=1)
  valMean = values[base].mean(axis=1)
  valStd = values[base].std(axis=1)
#  print name,base,valMean
#  print name,base,valStd
  leg2 = ax2.plot(values[base].mean(axis=1),paramBase[base],label=baseMap[base],c=colB)
  ax2.plot(valMean-valStd,paramBase[base],'--',label=baseMap[base],c=colB,lw=2,alpha=0.7)
  ax2.plot(valMean+valStd,paramBase[base],'--',label=baseMap[base],c=colB,lw=2,alpha=0.7)
  ax2.fill_betweenx(paramBase[base],valMean-valStd , valMean+valStd, color=colB, alpha=0.3)
  iKtrue = np.where(np.abs(Nmean-30)<2)
  if not name == '$K$':
    ax2.plot(values[base].mean(axis=1)[iKtrue],paramBase[base][iKtrue],'x',mew=4,ms=15,label=baseMap[base]+' $K={}$'.format(Nmean[iKtrue]),c=colorScheme('labelMap')['red'])
  ax2.set_ylabel(paramName[base],color=colB)  
  for  tl in ax2.get_yticklabels():
    tl.set_color(colB)
  tiks = ax2.get_yticks()
  tikLbl = ax2.get_yticklabels()
  tikLbl = [''] 
  tikLbl += [str(tik) for tik in tiks[1:]] 
  ax2.set_yticklabels(tikLbl)
  ax2.set_ylim(paramBase[base].min(),paramBase[base].max())
  if name == 'NMI':
    tiks = ax2.get_xticks()
    tikLbl = []
    for tik in tiks[::2]:
      tikLbl += [str(tik),'']
    del tikLbl[-1]
    ax2.set_xticklabels(tikLbl)
  if not showLeg is None and showLeg:
    legs = leg2+leg1
    labs = [leg.get_label() for leg in legs]
    ax2.legend(legs,labs,loc='best',prop={'size':legendSize})
  plt.tight_layout()
  plt.subplots_adjust(right=0.85,bottom=0.3)
  plt.savefig(cfg['outName']+'_{}.pdf'.format(re.sub('\$','',name)),figure=fig)
 

plotOverParams(mis,'MI',showLeg=False)
plotOverParams(nmis,'NMI',showLeg=False)
plotOverParams(Ns,'$K$',showLeg=True)
plotOverParams(Sils,'silhouette',showLeg=False)

plt.show()

#fig = plt.figure(figsize=figSize, dpi=80, facecolor='w', edgecolor='k')
#ax1 = plt.subplot(111)
#base = 'spkm'
#ax1.plot(Sils[base].mean(axis=1),paramBase[base],label=baseMap[base],c=cl[(0+1)*255/I])
#iKtrue = np.argmin(np.abs(Ns[base].mean()-30))
#ax1.plot(Sils[base].mean(axis=1)[iKtrue],paramBase[base][iKtrue],'x',label=baseMap[base]+' $K={}$'.format(Ns[base][iKtrue]),c=(1,0,0))
#ax1.set_ylabel(paramName[base])  
#ax1.invert_yaxis()
#ax1.set_xlabel("Sil")  
#ax1.legend(loc='best')
#ax2 = ax1.twinx()
#base = 'DPvMFmeans'
#ax2.plot(Sils[base].mean(axis=1),paramBase[base],label=baseMap[base],c=cl[(1+1)*255/I])
#iKtrue = np.argmin(np.abs(Ns[base].mean()-30))
#ax2.plot(Sils[base].mean(axis=1)[iKtrue],paramBase[base][iKtrue],'x',label=baseMap[base]+' $K={}$'.format(Ns[base][iKtrue]),c=(1,0,0))
#ax2.set_ylabel(paramName[base])  
#ax2.legend(loc='right')
#plt.tight_layout()
#plt.savefig(cfg['outName']+'_Sil.png',figure=fig)

#fig = plt.figure(figsize=figSize, dpi=80, facecolor='w', edgecolor='k')
#ax1 = plt.subplot(111)
#base = 'spkm'
#ax1.plot(Ns[base].mean(axis=1),paramBase[base],label=baseMap[base],c=cl[(0+1)*255/I])
#ax1.plot([30]*len(paramBase[base]), paramBase[base], label="true number of clusters $K=30$", c=(1,0,0))
#ax1.set_ylabel(paramName[base])  
#ax1.invert_yaxis()
#ax1.set_xlabel("number of clusters")  
#ax1.legend(loc='best')
#ax2 = ax1.twinx()
#base = 'DPvMFmeans'
#ax2.plot(Ns[base].mean(axis=1),paramBase[base],label=baseMap[base],c=cl[(1+1)*255/I])
#ax2.set_ylabel(paramName[base])  
#ax2.legend(loc='right')
#plt.tight_layout()
#plt.savefig(cfg['outName']+'_nClusters.png',figure=fig)


fig = plt.figure(figsize=figSize, dpi=80, facecolor='w', edgecolor='k')
for i,base in enumerate(bases):
  plt.subplot(1,2,i+1)
  plt.plot(paramBase[base],vMeasures[base][:],label=baseMap[base],c=cl[(i+1)*255/I])
  plt.title(base)
  plt.xlabel(paramName[base])
  plt.ylabel('vMeasure')
  plt.ylim([0,1])
  plt.legend(loc='lower right')
plt.tight_layout()
plt.savefig(cfg['outName']+'_VMeasure.png',figure=fig)

#fig = plt.figure(figsize=figSize, dpi=80, facecolor='w', edgecolor='k')
#for i,base in enumerate(bases):
#  plt.subplot(1,2,i+1)
#  plt.plot(paramBase[base],mis[base][:,-1],label=baseMap[base],c=cl[(i+1)*255/I])
#  plt.title(base)
#  plt.xlabel(paramName[base])
#  plt.ylabel('MI')
#  plt.legend(loc='lower right')
#plt.tight_layout()

fig = plt.figure(figsize=figSize, dpi=80, facecolor='w', edgecolor='k')
ax1 = plt.subplot(111)
base = 'spkm'
ax1.plot(mis[base][:],paramBase[base],label=baseMap[base],c=cl[(0+1)*255/I])
ax1.set_ylabel(paramName[base])  
ax1.invert_yaxis()
ax1.set_xlabel("MI")  
ax1.legend(loc='best')
ax2 = ax1.twinx()
base = 'DPvMFmeans'
ax2.plot(mis[base][:],paramBase[base],label=baseMap[base],c=cl[(1+1)*255/I])
ax2.set_ylabel(paramName[base])  
ax2.legend(loc='right')
plt.tight_layout()
plt.savefig(cfg['outName']+'_MI.png',figure=fig)

#fig = plt.figure(figsize=figSize, dpi=80, facecolor='w', edgecolor='k')
#for i,base in enumerate(bases):
#  plt.subplot(1,2,i+1)
#  plt.plot(paramBase[base],Ns[base][:,-1],label=baseMap[base],c=cl[(i+1)*255/I])
#  plt.title(base)
#  plt.xlabel(paramName[base])
#  plt.ylabel('number of clusters')
#  plt.legend(loc='best')
#plt.tight_layout()


plt.show()
