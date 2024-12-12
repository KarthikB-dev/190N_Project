sudo -v

ansible-playbook -i ./190n-inf-key/inventory.ini ./ansible/guacamole.yml

ansible-playbook -i ./190n-inf-key/inventory.ini ./ansible/vpn.yml

exit 0

sudo -v
cd ansible/files/vpn

# Run openvpn in background
sudo openvpn --config client.conf &

cd ../../..
# Execute
sleep 5
ansible-playbook -i ./190n-inf-key/inventory.ini ./ansible/ghosts.yml

# Kill openvpn by pid
sudo kill $!
