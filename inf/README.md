# AWS NATwork
This is a testing environment that simulates a NAT network on AWS.

## Deployment
### Prerequisites
- Terraform
- Ansible
- OpenVPN

And of course a debian-like OS.

### Steps
1. `cd` into the `inf` directory
2. Run `terraform init`
3. Run `terraform apply`
4. Check for any running OpenVPN instances, kill them if they are leftover from a previous run
5. Run `deploy.sh` to deploy the software on the instances
6. Run `start.sh` to start capturing the traffic
7. Run `stop.sh` to stop capturing the traffic
8. Review the traffic saved as `wan.pcap` and `lan.pcap` in the `inf` directory


## Acknowledgments
This part of the project is highly inspired by, and some components are based on, the GATE (Globally Accessible Testing Environment)
of the [ACTION institute](https://action.ucsb.edu/). **None of the code in this section should be openly shared or distributed without the explicit permission of the ACTION institute**