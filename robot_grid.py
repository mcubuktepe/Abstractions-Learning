from gridworld import Gridworld
import numpy as np
from mdp import MDP
from tqdm import tqdm
def get_indices_of_k_smallest(arr, k):
    idx = np.argpartition(arr.ravel(), k)
    return tuple(np.array(np.unravel_index(idx, arr.shape))[:, range(min(k, 0), max(k, 0))])

def writeJson(outfile,my_dict=None):
    with open(outfile, 'w') as f:
        [f.write('{0},{1}\n'.format(key, value)) for key, value in my_dict.items()]

num_x = 20
num_y = 20
num_t = 20
max_x = 600
min_x = -600
max_y = 600
min_y = -600
xrange = np.linspace(min_x,max_x,num_x)
yrange = np.linspace(min_y,max_y,num_y)
trange = np.linspace(0+360.0/num_t,360,num_t)
traterange = [-2,0,2]
transitions = []
states = []
dt = 4
v = 25

ballpos = (xrange[4],yrange[4])
targ_angle = trange[4]
angle_uncertainty = 0.1
uncertainty_disc = 3

R = dict()
for x in tqdm(xrange):
    for y in yrange:
        for t in trange:
            states.append((x, y, t))

            # poss_t = list(np.linspace(t - angle_uncertainty, t + angle_uncertainty, angle_uncertainty_disc))

            for trate in traterange:
                if (x, y, t) == ballpos + tuple({targ_angle}):
                    transitions.append(((x, y, t), trate, (x, y, t), 1.0))
                    R[((x, y, t), trate, (x, y, t))] = 0
                elif (abs(x) > 450 or abs(y) > 450) or (y >= ballpos[1] and abs(x) <= 300):
                    transitions.append(((x, y, t), trate, (x, y, t), 1.0))
                    R[((x, y, t), trate, (x, y, t))] = -10
                else:
                    transdict = dict([((x, y, t), trate, (xnew, ynew, tnew)), 0.0] for xnew in xrange for ynew in yrange for tnew in trange)
                    next_t =  t + dt*trate
                    next_t = next_t % 360
                    next_x = max(min(max_x,x+v*dt*np.cos(np.radians(next_t))),min_x)
                    next_y = max(min(max_y,y + v*dt*np.sin(np.radians(next_t))),min_y)
                    xs = np.full((len(xrange)), next_x)
                    ys = np.full((len(yrange)), next_y)
                    ts = np.full((len(trange)), next_t)
                    indkeysetx = get_indices_of_k_smallest(np.abs(xrange - xs), uncertainty_disc)[0]
                    indkeysety = get_indices_of_k_smallest(abs(yrange - ys), uncertainty_disc)[0]
                    indkeysett = get_indices_of_k_smallest(abs(trange - ts) - ts, 1)[0]
                    w = []
                    for nx in indkeysetx:
                        for ny in indkeysety:
                            for nt in indkeysett:
                                transdict[((x, y,t), trate, (xrange[nx], yrange[ny],trange[nt]))] += 1.0/(len(indkeysetx)+len(indkeysety)+len(indkeysett))
                    for x2 in xrange:
                        for y2 in yrange:
                            for t2 in trange:
                                if transdict[(x,y,t),trate,(x2,y2,t2)] > 0:
                                #     if abs(x2) > 800 or abs(y2) > 800 or (y2>ballpos[1] and abs(x2) < 500):
                                #         R[((x, y, t), trate, (x2, y2, t2))] = -10
                                #     # elif (x2, y2, t2) == ballpos + tuple({targ_angle}):
                                #     #     R[((x, y, t), trate, (x2, y2, t2))] = 1
                                #     # elif (x, y, t) == ballpos + tuple({targ_angle}):
                                #     #     R[((x, y, t), trate, (x2, y2, t2))] = 0
                                #     else:
                                    R[((x, y, t), trate, (x2, y2, t2))] = -1
                                    transitions.append(((x,y,t),trate,(x2,y2,t2),transdict[(x,y,t),trate,(x2,y2,t2)]))

alphabet = traterange
robot_mdp = MDP(states,alphabet,transitions)


# R = dict.fromkeys(transdict.keys(),-1)
# for x in tqdm(xrange):
#     for y in yrange:
#         for t in trange:
#             for trate in traterange:
#                 for x2 in xrange:
#                     for y2 in yrange:
#                         for t2 in trange:
#                             if abs(x2) > 800 or abs(y2) > 800:
#                                 R[((x,y,t),trate,(x2,y2,t2))] = -10
#                             elif (x,y,t) == ballpos+tuple({targ_angle}):
#                                 R[((x, y, t), trate, (x2, y2, t2))] = 10

print('Computing policy...')
V, policy = robot_mdp.max_reach_prob({ballpos + tuple({targ_angle})})
print policy
print V
writeJson('robotpolicy_E',policy)