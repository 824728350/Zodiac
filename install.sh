sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install zip
sudo pip3 install z3
sudo pip3 install wget
sudo pip3 install python-hcl2
sudo apt-get update && sudo apt-get install -y gnupg software-properties-common
wget -O- https://apt.releases.hashicorp.com/gpg | \
gpg --dearmor | \
sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null
gpg --no-default-keyring \
--keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg \
--fingerprint
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update
sudo apt-get install terraform
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
wget https://github.com/fugue/regula/releases/download/v3.2.1/regula_3.2.1_Linux_x86_64.tar.gz
tar -zxvf regula_3.2.1_Linux_x86_64.tar.gz
rm -rf regula_3.2.1_Linux_x86_64.tar.gz
sudo mv regula /usr/local/bin
curl -L -o opa https://openpolicyagent.org/downloads/v0.67.1/opa_linux_amd64_static
sudo chmod 777 opa
sudo mv opa /usr/local/bin
git clone https://github.com/jacobgelling/EdgeGPT.git
