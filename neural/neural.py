import numpy as np
import random

class NN:
    def __init__(self, shape, dna=None):
        self.shape = shape
        self.w = []
        if dna is None:
            self.gen_weights()
        else:
            self.dna(dna)

    def gen_weights(self, random=True):
        self.w = []
        for i in range(len(self.shape) -1):
            w = np.zeros((self.shape[i+1] + 1, self.shape[i] + 1))
            if random:
                w[:-1] = np.random.random((self.shape[i+1], self.shape[i]+1)) * 2 -1
            w[-1, -1] = 1
            
            self.w.append(w)

    def process(self, data):
        try:
            l = len(data)
        except TypeError:
            # dado nao em uma lista
            l = 1
            data = [data]
        finally:
            if l != self.shape[0]:
                raise TypeError('entrada com tamanho diferente to esperado')

        z = np.concatenate((data, [np.ones_like(data[0])]))

        for w in self.w[:-1]:
            z = self.foward(w, z, func=self.relu)
        z = self.foward(self.w[-1], z, func=None)
        
#         if self.shape[0] == 1:
#             return np.squeeze(z[:-1])
#         else:
#             return z[:-1]
        return z[:-1]
                                 
    def foward(self, w, z, func=None):
        z = np.dot(w, z)
        if func is not None:
            z[:-1] = func(z[:-1])
        return z
    
    def sigmoid(self, z):
        return 1/(1+np.exp(-z))
    
    def relu(self, z):
        z[z<0] = 0
        return z
    
    def softplus(self, z):
        return np.log(1 + np.exp(z))
    
    def softmax(self, z):
        return z/self.sum(z)
    
    def sum(self, z):
        return np.sum(z, axis=0)
    
    def dna(self, dna=None):
        if dna is None:
            # retorna os parametros como uma lista
            return np.concatenate([w[:-1].reshape(-1) for w in self.w])
        else:
            # atribui os parametros a partir de um lista
            dna = np.array(dna)
            self.gen_weights(random=False)
            i = 0
            for j in range(len(self.shape) -1):
                new_i = i + (self.shape[j]+1)*self.shape[j+1]
                self.w[j][:-1] = dna[i:new_i].reshape(self.shape[j+1], -1)
                i = new_i

class Pop():
    def __init__(self, species, size, **kwargs):
        self.species = species
        self.size = size
        self.pop = [species(**kwargs) for _ in range(size)]
        self.fitness = []
        self.gen = 0

    def next_gen(self):
        self.gen += 1
        total_fit = sum(self.fitness)
        prob = [fit/total_fit for fit in self.fitness]
        
        self.pop = [self.species(self.pop[0].shape, self.sex2(prob)) for _ in range(self.size)]

    def sex(self, weights):
        parents = random.choices(self.pop, weights=weights, k=2)
        parents = [p.dna() for p in parents]
        select = np.random.randint(0,2, len(parents[0]))
        child = [parents[select[i]][i] for i in range(len(parents[0]))]
        # mutacao
        self.mutate(child)
        return child
    
    def sex2(self, weights):
        parents = random.choices(self.pop, weights=weights, k=2)
        parents = [p.dna() for p in parents]
        cut = random.randint(0, len(parents[0]))
        child = np.concatenate((parents[0][:cut], parents[1][cut:]))
        # mutacao
        self.mutate(child)
        return child
           
    def mutate(self, child):
        if random.random() < 0.02:
            i = random.randint(0, len(child)-1)
            child[i] += np.random.randn()

def chi2(x, y, pop):
    fit  = []
    for c in pop.pop:
        yy = [c.process([i])[0] for i in x]
        fit.append(1/np.sum((yy-y)**2))
    pop.fitness = fit
    
def aic(x, y, pop):
    n = len(y)
    p = pop.pop[0].shape[0]
    fit = []
    for c in pop.pop:
        yy = [c.process([i])[0] for i in x]
        s = np.sum((yy - y)**2)/(n - p - 1)
        fit.append(n*np.log(s) + 2*p)
    pop.fitness = fit
    
def chimean(x, y, pop):
    fit = []
    for c in pop.pop:
        yy = yy = [c.process([i])[0] for i in x]
        s = np.sum((yy - y)**2)
        ym = np.mean(yy)
        sm = np.sum((yy - ym)**2)
        print(sm, s)
        fit.append(1 - s/sm)
    pop.fitness = fit