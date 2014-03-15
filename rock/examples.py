from rock import rock;
from support import read_sample;
from support import draw_clusters;
from support import timedcall;

def template_clustering(path, radius, cluster_numbers, threshold, draw = True):
    sample = read_sample(path);
    
    (ticks, clusters) = timedcall(rock, sample, radius, cluster_numbers, threshold);
    print("Sample: ", path, "\t\tExecution time: ", ticks, "\n");
    
    if (draw == True):
        draw_clusters(sample, clusters);
    
def cluster_simple1():
    template_clustering('../samples/SampleSimple1.txt', 1, 2, 0.5);
    
def cluster_simple2():
    template_clustering('../samples/SampleSimple2.txt', 1, 3, 0.5);
    
def cluster_simple3():
    template_clustering('../samples/SampleSimple3.txt', 1, 4, 0.5);
    
def cluster_simple4():
    template_clustering('../samples/SampleSimple4.txt', 1, 4, 0.5);
    
def cluster_elongate():
    template_clustering('../samples/SampleElongate.txt', 1, 2, 0.5); 
    
def cluster_lsun():
    template_clustering('../samples/SampleLsun.txt', 1, 3, 0.5);       

def cluster_target():
    template_clustering('../samples/SampleTarget.txt', 1.2, 6, 0.2);     

def cluster_two_diamonds():
    template_clustering('../samples/SampleTwoDiamonds.txt', 0.2, 2, 0.2);  

def cluster_wing_nut():
    template_clustering('../samples/SampleWingNut.txt', 0.3, 2, 0.2); 
    
def cluster_chainlink():
    template_clustering('../samples/SampleChainlink.txt', 0.6, 2, 0.2);     
    
def cluster_hepta():
    template_clustering('../samples/SampleHepta.txt', 1.2, 7, 0.2); 
    
def cluster_tetra():
    template_clustering('../samples/SampleTetra.txt', 0.5, 4, 0.2);  
    
def experiment_execution_time():
    template_clustering('../samples/SampleSimple1.txt', 1, 2, 0.5, False);
    template_clustering('../samples/SampleSimple2.txt', 1, 3, 0.5, False);
    template_clustering('../samples/SampleSimple3.txt', 1, 4, 0.5, False);
    template_clustering('../samples/SampleSimple4.txt', 1, 4, 0.5, False);
    template_clustering('../samples/SampleElongate.txt', 1, 2, 0.5, False);
    template_clustering('../samples/SampleLsun.txt', 1, 3, 0.5, False);
    template_clustering('../samples/SampleTarget.txt', 1.2, 6, 0.2, False);
    template_clustering('../samples/SampleTwoDiamonds.txt', 0.2, 2, 0.2, False);
    template_clustering('../samples/SampleWingNut.txt', 0.3, 2, 0.2, False);
    template_clustering('../samples/SampleChainlink.txt', 0.6, 2, 0.2, False);
    template_clustering('../samples/SampleHepta.txt', 1.2, 7, 0.2, False);
    template_clustering('../samples/SampleTetra.txt', 0.5, 4, 0.2, False);
    

cluster_simple1();
cluster_simple2();
cluster_simple3();
cluster_simple4();
cluster_elongate();
cluster_lsun();
cluster_target();
cluster_two_diamonds();
cluster_wing_nut();
cluster_chainlink();
cluster_hepta();
cluster_tetra();


#experiment_execution_time();