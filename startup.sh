#!/bin/bash

CS_BUCKET=$(curl http://metadata/computeMetadata/v1beta1/instance/attributes/cs-bucket)
CONDOR_DEBCONF=$(curl http://metadata/computeMetadata/v1beta1/instance/attributes/condor-debconf)


sudo apt-get udpate
echo "condor condor/wantdebconf boolean false" | sudo debconf-set-selections
sudo apt-get -q -y install condor

sudo gsutil -n update
gsutil cp gs://$CS_BUCKET/$CONDOR_DEBCONF ./00debconf
sudo mv 00debconf /etc/condor/config.d/
sudo /etc/init.d/condor restart

#example for adding extra software
#sudo apt-get -q -y install gfortran
