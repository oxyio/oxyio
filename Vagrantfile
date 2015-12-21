# Oxypanel
# File: Vagrantfile
# Desc: development VM & testing VM's (Ubuntu, Debian & CentOS)

Vagrant.configure('2') do |config|
    # Give the box enough memory
    config.vm.provider 'virtualbox' do |vbox|
        vbox.customize ['modifyvm', :id, '--memory', 1024]
    end

    # Sync dev folder
    config.vm.synced_folder './', '/opt/oxypanel'

    # Dev VM
    config.vm.define :dev, primary: true do |oxypanel|
        oxypanel.vm.hostname = 'oxypanel-dev'
        oxypanel.vm.box = 'ubuntu/trusty64'

        oxypanel.vm.provider 'virtualbox' do |vbox|
            vbox.name = 'oxypanel-dev'
        end

        # Expose an IP
        oxypanel.vm.network :private_network, ip: '13.13.13.13'

        # Install Oxypanel using local install.py with --debug
        oxypanel.vm.provision 'shell', path: './deploy/bootstrap.sh', args: ['--dev', '--debug']
    end

    # Ubuntu Trusty 14.04 test VM
    config.vm.define :ubuntu, autostart: false do |ubuntu|
        ubuntu.vm.hostname = 'oxypanel-ubuntu'
        ubuntu.vm.box = 'ubuntu/trusty64'
        ubuntu.vm.network :private_network, ip: '16.16.16.16'

        # Install Oxypanel using local install.py
        config.vm.provision 'shell', path: './deploy/bootstrap.sh', args: ['--dev']
    end

    # Debian Wheezy 7.5 test VM
    config.vm.define :debian, autostart: false do |debian|
        debian.vm.hostname = 'oxypanel-debian'
        debian.vm.box = 'puphpet/debian75-x64'
        debian.vm.network :private_network, ip: '17.17.17.17'

        # Install Oxypanel using local install.py
        config.vm.provision 'shell', path: './deploy/bootstrap.sh', args: ['--dev']
    end

    # Centos 6.5 test VM
    config.vm.define :centos, autostart: false do |centos|
        centos.vm.hostname = 'oxypanel-centos'
        centos.vm.box = 'chef/centos-6.5'
        centos.vm.network :private_network, ip: '18.18.18.18'

        # Install Oxypanel using local install.py
        config.vm.provision 'shell', path: './deploy/bootstrap.sh', args: ['--dev']
    end
end
