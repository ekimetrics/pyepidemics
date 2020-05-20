import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import pdb

def plot_data(real_cases,region_label):
  plt.figure()
  plt.plot(real_cases[:,0]-t0,real_cases[:,1])
  plt.title('cummulative ' + region_label + ' cases')


simulation_region="Shenzen"
brute_cases_shenzhen=[1,2,14,15,15,20,27,36,49,63,86,110,170,196,226,269,289,314,334]
dates_shenzhen=[19,21,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37]
shenzen_cases=np.vstack((np.array(dates_shenzhen).T,np.array(brute_cases_shenzhen).T)).T
t0=19
#plot_data(shenzen_cases,simulation_region)


simulation_region="Singapore"
brute_cases_singapore=[1,3,3,4,5,7,10,13,16,18,18,18,24,28,30,40]
dates_singapore=[23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,39]
singapore_cases=np.vstack((np.array(dates_singapore).T,np.array(brute_cases_singapore).T)).T
t0=23

#plot_data(singapore_cases,simulation_region)



simulation_region="Hong Kong"
hk_cases= np.array([[22,1,0],[23,2,0],[24,5,0],[25,5,0],[26,8,0],[27,8,0],[28,8,0],[29,10,0],
                    [30,12,0],[31,13,0],[32,14,0],[33,15,0],[34,15,0],[35,18,0],[36,21,0],
                    [37,24,0],[38,26,0],[39,26,0],[40,36,0],[41,42,0],[42,49,0],[43,50,0],
                    [44,53,0],[45,56,0],[46,56,0],[47,57,0],[48,60,0],[49,62,0],[50,65,0],
                    [51,69,0],[52,69,0],[53,70,0],[54,74,0],[55,79,0]])

'''hk_cases= np.array([[22,1,1],[23,2,2],[24,5,5],[25,5,5],[26,8,8],[27,8,8],[28,8,8],[29,10,10],
                    [30,12,12],[31,13,13],[32,14,14],[33,15,15],[34,15,15],[35,18,18],[36,21,21],
                    [37,24,24],[38,26,26],[39,26,26],[40,36,36],[41,42,42],[42,49,49],[43,50,50],
                    [44,53,53],[45,56,56],[46,56,56],[47,57,57],[48,60,60],[49,62,62],[50,65,65],
                    [51,69,69],[52,69,69],[53,70,70],[54,74,74],[55,79,79]])'''

t0=22 #start Jan 22
#plot_data(hk_cases,simulation_region)
proportion = 0.9
N = np.array([7.5*1000*1000*proportion,7.5*1000*1000*(1-proportion)])
N_tot = np.sum(N)
simulation_choice={"t0":22,"label":"Hong Kong","N":N, "real_cases":hk_cases,"M_contact": np.array([[proportion,proportion],[1-proportion,1-proportion]]), "N_group":2, "N_tot" : N_tot }





########Initialization of parameters################
# Total population, N
N=simulation_choice["N"]
t0=simulation_choice["t0"]
real_cases=simulation_choice["real_cases"].copy()

# Initial values I0 and R0.
L0,I0,A0,D0,R0= np.array([0.,0.]),np.array([10*proportion,10*(1-proportion)]),np.array([10*proportion,10*(1-proportion)]),np.array([0.,0.]),np.array([0.,0])
# S0 is the rest
S0 = N-L0-I0-A0-D0-R0
gammaL= 1/3.0 # time in the latent non infectious phase
gammaI,gammaA = 1/2.5, 1/5.0 #time to detection or end of infectious phase
beta = .4
delta=1.0 #how infectious is the low danger phase = beta(A)/beta(I)
p=0.1 #probability to have a high danger form
initial_guess_params=(N,beta,gammaL,delta,p,gammaI,gammaA,simulation_choice["M_contact"], simulation_choice["N_group"])

# Initial conditions vector
initial_guess_y0 = [list(S0),list(L0),list(I0),list(A0),list(D0),list(R0)]
initial_guess_y0 = [item for sublist in initial_guess_y0 for item in sublist]
initial_guess_y0 = tuple(initial_guess_y0)
#############end initialization#############

# A grid of time points (in days)
t = np.linspace(0, 160, 160)

# The SLIADRE model differential equations.
def deriv(y, t, N,beta,gammaL,delta,p,gammaI,gammaA,M_contact,N_group):
    """ 
    the model takes as input a tuple of initial values and constructs the derivative
    """
    S = y[:N_group]
    L = y[1*N_group: 1*N_group+2]
    I = y[2*N_group: 2*N_group+2]
    A = y[3*N_group: 3*N_group+2]
 
    V = np.zeros(N_group)

    for nk in range(N_group):
        V[nk] = beta*S[nk]*(I[nk]+delta*A[nk])/N[nk]

    dSdt, dLdt,dIdt,dAdt, dDdt,dRdt = np.zeros(N_group),np.zeros(N_group),np.zeros(N_group),np.zeros(N_group),np.zeros(N_group),np.zeros(N_group)

    for nk in range(N_group):
        dSdt[nk]= - np.sum(M_contact[nk,:]*V)
        dLdt[nk] = - dSdt[nk] - gammaL *L[nk]
        dIdt[nk] = p*gammaL*L[nk] - gammaI*I[nk]
        dAdt[nk] = (1-p)*gammaL*L[nk] - gammaA*A[nk]
        dDdt[nk] = gammaI*I[nk]
        dRdt[nk] = gammaA*A[nk]

    diff = [list(dSdt),list(dLdt),list(dIdt),list(dAdt),list(dDdt),list(dRdt)]
    diff = [item for sublist in diff for item in sublist]

    return tuple(diff)

def myplot():
    plt.figure(32,figsize=(16,8))

    plt.subplot(2,4,1)
    plt.plot(t,S/N[1],"b")
    plt.legend(["Susceptible"])
    plt.xlabel('Time (days)')

    plt.subplot(2,4,2)
    plt.plot(t,L,"r")
    plt.legend(["Latent"])
    plt.xlabel('Time (days)')

    plt.subplot(2,4,3)
    plt.plot(t,I,"r")
    plt.legend(["Infected"])
    plt.xlabel('Time (days)')

    plt.subplot(2,4,4)
    plt.plot(t,A,"r")
    plt.legend(["Aternative"])
    plt.xlabel('Time (days)')

    plt.subplot(2,4,5)
    plt.plot(t,R,"g")
    plt.legend(["Removed"])
    plt.xlabel('Time (days)')

    plt.subplot(2,4,6)
    plt.plot(t,D,"r",real_cases[:,0]-t0,real_cases[:,1],"x")
    plt.legend(["Detected",simulation_choice["label"] + " cases"])
    plt.xlabel('Time (days)')

    plt.savefig("figure2.png")
    plt.savefig("figure2.pdf")
    plt.show()



    #test from initial conditions
# Integrate the SIR equations over the time grid, t.
print('initial_guess_params=',initial_guess_params)
ret = odeint(deriv, initial_guess_y0, t, args=initial_guess_params)
results = ret.T

S = results[1]
L = results[3]
I = results[5]
A = results[7]
D = results[9]
R = results[11]
myplot()
print(results[:2])
print(S)
