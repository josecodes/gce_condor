#GceCondor

A class that helps set up and shutdown a simple Condor cluster on Google Compute Engine (GCE)

MIT's excellent Starcluster library was used as inspiration for starting this, although this just a teeny-tiny subset of
 that functionality. One day Starcluster may support GCE, but for now I am using these simple scripts.

A basic summary:  *gce_condor.py* uses *startup.sh* as a start up script for the GCE instance.  *startup.sh* installs
 condor using debian's apt-get installer and then puts the master and node debian configuration files on the appropriate
 instances.


##Installation

1. Upload *startup.sh*, *master_00debconf*, and *node_00debconf* to your Google Cloud Storage Bucket.
2. In *gce_condor.py*, set `PROJECT_ID` to the name of your project and `CS_BUCKET` to the name of your bucket.

##Usage

Before you run gce_condor, you will need to have created a *client_secrets.json* file and placed it in the same
 directory. Directions for creating the *clients_secrets.json* file are [here][1].






[1] https://developers.google.com/compute/docs/api/python_guide#authorization
