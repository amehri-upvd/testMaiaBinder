#!/usr/bin/env python
# coding: utf-8

# ### Step 1 
# 
# Maia is a parallel application ! Almost every function require an MPI communicator, so we first
# need to import the so called COMM_WORLD communicator from mpi4py.
# 
# -> Get the communicator, print the rank of the current process and launch the program
# using mpirun

# In[229]:


from mpi4py import MPI
comm = MPI.COMM_WORLD


# ### Step 2
# 
# Maia is a Python/C++ library providing a parallel framework to apply various algorithms over CGNSTrees.
# Especially, 
#  - Maia extends the CGNS Standard to describe trees in a MPI context
#  - Maia provides some algorithms that can be applied to these trees
# 
# First, open the documentation which will be helpful in this TP :
# https://onera.github.io/Maia/1.3/index.html
# Have a quick look to the definition of parallel CGNSTree (Introducion > Maia CGNS Tree)
# and to the organisation of the different modules (UserManual)
# 
# -> Then, import the maia package

# In[230]:


import maia
import numpy as np
import maia.pytree as PT

np.printoptions(precision=3, suppress=True)


# ### Step 3 -- File reading
# 
# -> Read the CGNSFile from the disk using the main maia.io reading function : 
# file_to_dist_tree. Is the output a DistTree or PartTree ?
# 
# -> Check your answer by printing the tree with maia.pytree.print_tree(tree)

# In[231]:


FILENAME = 'rotor37_small.cgns'
tree = maia.io.file_to_dist_tree(FILENAME, comm)
PT.print_tree(tree)


# ### Step 4 -- 360° duplication
# 
# The mesh we are working with is an angular section of the famous rotor 37 blade.
# In this step, we want to recover the full geometry using a duplication.
# 
# Search in the documentation which function(s) must be called to perfom this operation.
# Check carefully if this function which kind of parallel tree this function expects
# to work with.
# 
# -> This function takes as an input the paths of the GridConnectivity_t nodes that define
# the periodic transformation. What is wrong with this mesh ?
# 
# [! Spoiler !]
# 
# Our mesh has no GridConnectivities ! Apparently, ANSA did not store it and we need to
# recover it.
# 
# Step 4a -- Recovering GC_t
# 
# In fact, the concerned boundary faces are stored in two BC_t nodes : perleft_1 and perright_1
# -> Read the documentation of connect_1to1_families and call it to rebuild the 1to1 connections
# HINT : The rotation angle to go from perleft to perright is 2*pi/36
# -> Then check the presence of GC_t in the tree and note their path.

# In[232]:


maia.algo.dist.connect_1to1_families(tree, ('perleft', 'perright'), 
                                     comm,
                                     periodic={'rotation_angle' : np.array([float(2*np.pi/36.),0.,0.])})
PT.print_tree(tree)


# ### Step 4b -- 360° Field initialization (bonus)
# 
# In order to illustrate the ability of the duplication to move the vectorial fields
# together with the mesh, we are going to create a initial field in the input zone.
# 
# -> Get the coordinates x,y, and z of the input zone.
# 
# -> Compute a the following vertex located velocity :
# ```python
#    vx = α 
#    vy = -α*sin(Θ)     where α = sqrt(2)/2
#    vz = α*cos(Θ)            Θ = atan(z/y)
#    ```
# This correspond to the uniform field $α(ux + uΘ)$ in the cylindric coordinates.
# 
# -> Add the fields in a FlowSolution container. Be carefull end your the names
#    by X,Y and Z to have it considered as a vectorial field later.

# In[233]:


gc_x = PT.get_node_from_name(tree,"CoordinateX")
gc_y = PT.get_node_from_name(tree,"CoordinateY")
gc_z = PT.get_node_from_name(tree,"CoordinateZ")
x = np.array(PT.get_value(gc_x))
y = np.array(PT.get_value(gc_y))
z = np.array(PT.get_value(gc_z))


# In[234]:


alpha = np.sqrt(2)/2.
theta = np.arctan(z/y)
vx = np.full(len(x), alpha)
vy = - alpha * np.sin(theta)
vz = alpha * np.cos(theta)

vx,vy,vz


# In[235]:


velocity_fields = {'VelocityX' : vx,
                   'VelocityY' : vy,
                   'VelocityZ' : vz,
                   }
fs_node = PT.new_FlowSolution('FlowSolution#Uniform', fields = velocity_fields)
PT.print_tree(fs_node)


# In[236]:


zone_node = PT.get_all_Zone_t(tree)[0]
PT.add_child(zone_node, fs_node)
PT.print_tree(tree)


# ### Step 4c -- 360° duplication
# 
# Now that tree has periodic joins, we can call the duplication function.
# - Use the paths of the GC_t created nodes to call the duplication function
# - Check the number of Zone_t registered in the tree after the duplication
# 
# > IMPORTANT : 
# > If you are doing this TP in interractive mode, the size of the large mesh
# > after a 360° will be to high to fit on a computing node. You can skip this
# > step or replace the duplication function by maia.algo.dist.duplicate_from_periodic_jns
# > In this case, add the number of wanted duplication (no more than 2)
# > before the 'comm' argument

# In[237]:


gc_nodes = PT.get_nodes_from_label(tree, "GridConnectivity_t")
# for node in gc_nodes: 
#     print(">>>", node[0])
#     PT.print_tree(node)
    
zone_paths = ["Base/Rotor"]
left_jns   = ["Base/Rotor/ZoneGridConnectivity/perleft_0"]
right_jns  = ["Base/Rotor/ZoneGridConnectivity/perright_0"]

[PT.get_node_from_path(tree,jn_path_a) for jn_path_a in left_jns]
maia.algo.dist.duplicate_from_periodic_jns(dist_tree         = tree,
                                           zone_paths        = zone_paths,
                                           jn_paths_for_dupl = (left_jns, right_jns),
                                           dupl_nb = 2,
                                           comm = comm)

PT.print_tree(tree)


# ### Step 5 -- Merging zones
# 
# As you noticed, the tree has now several physical zones (due to the duplication).
# Sometimes it can be usefull to merge these zones, which are still connected throught
# 1to1 matching joins, into a single one, for example:
# - to call a tool that does not manage multiblock meshes (e.g. mesh adaptation)
# - to avoid interface management in the solver
# 
# Search in the documention the function to call to merge the zones. Again, verify that
# it works with distributed trees.
# 
# -> call the function and check again the number of Zone_t in the output tree

# In[238]:


# zone_pred = lambda x: PT.get_all_Zone_t(tree)
# PT.predicates_to_paths(tree, zone_pred)
maia.algo.dist.merge_zones(tree, ["Base/Rotor.D0", "Base/Rotor.D1", "Base/Rotor.D2"], comm)
PT.print_tree(tree)


# ### Step 6 : Mesh is ready ! Write it in file and use ParaView to visualize it

# In[239]:


# maia.io.dist_tree_to_file(tree, "output_"+FILENAME, comm)


# Now you can try it on the large mesh, with a suitable suitable number of processes (use sbatch !)
# For a "no solver" workflow, a rule of thumb is 1 to 2M of cells per MPI rank.

# ### Step 7 -- Computing wall distance
# 
# In order to prepare a RANS computation, distance to the wall are needed by the solver.
# Maia is able to compute theses distance in a parallel context.
# Search in the documentation the relevant function. Why can we not apply it directly ?
# [! Spoiler !]
# This function operates on partitioned trees ! Sounds like it's time to learn about
# partitioning.
# 
# The functions we used before were located in the algo module, since they did not change
# the parallel kind of our tree. The partitioning operation is different : the kind of the
# input (distributed tree) is transformed (partitioned tree). This function can thus be
# found in the factory module.
# 
# - Call the partitioning function with its default settings
# - Print the tree (maia.pytree.print_tree). Can you notice the differences with the distributed tree ?

# In[240]:


part_tree = maia.factory.partition_dist_tree(tree, comm)
maia.algo.part.compute_wall_distance(part_tree, comm)
PT.print_tree(part_tree)


# ### Step 8 -- Computing wall distance (for real :-) )
# 
# Now we have two parallel visions of the same mesh :
# one in the distributed layout, one in the partitioned layout.
# - Call the wall distance computation on the good tree
# 
# > NOTE : if you encounter runtime failure, you can try to
# > set the env. variable PDM_DIST_CLOUD_SURF_OPTIM to 1, or
# > to reduce the number of duplications.

# In[241]:


maia.io.part_tree_to_file(part_tree, "walld_"+FILENAME, comm)


# ### Step 9 -- Slice
# 
# The previous function should have created a FlowSolution_t container called WallDistance
# on the partionned tree. 
# To finish this mini tp, we will produce a 2D slice of the mesh and get this container on
# the slice (as we would do for solver computed fields)
# - Search in the documentation how to create a slice for the plane of equation x = 0.025
# and call the releveant function. What is the kind of the output tree ?

# In[242]:


slice_tree = maia.algo.part.plane_slice(part_tree, 
                                        plane_eq = [0,0,1,0.5], 
                                        comm     = comm, 
                                        containers_name=["WallDistance"])


# ### Step 10 -- Saving the slice
# 
# At this point, we have
# - For the volumic tree, a distributed and a partitioned vision
# - For the slice tree, a partitioned vision
# Since the slice is a partitioned tree, we can not directly write it with
# maia.io.dist_tree_to_file : we could use partitioned IO, but this would let some tracks
# of partitioning in the output file (such as several CGNS Zone_t)
# 
# In order to use distributed io, we first need to perform the opposite operation of 
# the partitioning function : we want to create a distributed view of the slice tree.
# As partition_dist_tree, such a function changes the parallel vision of its argument
# and can thus be found in the factory module.
# -> Call recover_dist_tree on the partitioned slice to get the distributed counterpart of
# the slice tree
# -> Then, save the slice in a CGNSFile using distributed IO

# In[243]:


maia.factory.recover_dist_tree(slice_tree, comm)
PT.print_tree(slice_tree)


