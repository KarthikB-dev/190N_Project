ansible-playbook -i ./190n-inf-key/inventory.ini ./ansible/guacamole.yml


exit 1

ansible-playbook -i ./190n-inf-key/inventory.ini ./ansible/vpn.yml

cd ansible/files/vpn

# Run openvpn in background
sudo openvpn --config client.conf &

cd ../../..
# Execute
sleep 5

# Kill openvpn by pid
sudo kill $!
