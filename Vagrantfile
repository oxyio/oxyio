# Oxypanel
Vagrant.configure('2') do |config|
    # Dev VM
    config.vm.define :dev, primary: true do |oxypanel|
        oxypanel.vm.hostname = 'oxypanel-dev'
        oxypanel.vm.box = 'ubuntu/precise64'
        oxypanel.vm.box_url = 'http://files.vagrantup.com/precise64.box'

        # Give the box enough memory
        oxypanel.vm.provider 'virtualbox' do |vbox|
            vbox.name = 'oxypanel'
            vbox.customize ['modifyvm', :id, '--memory', 1024]
        end

        # Expose an IP
        oxypanel.vm.network :private_network, ip: '13.13.13.13'

        # Sync dev folder
        oxypanel.vm.synced_folder './', '/opt/oxypanel'

        # Install Oxypanel
        oxypanel.vm.provision 'shell', path: './deploy/bootstrap.sh', args: 'dev'
    end

    # Test VM
    config.vm.define :test, primary: true do |test|
        test.vm.hostname = 'oxypanel-test'
        test.vm.box = 'ubuntu/precise64'
        test.vm.box_url = 'http://files.vagrantup.com/precise64.box'

        # Give the box enough memory
        test.vm.provider 'virtualbox' do |vbox|
            vbox.name = 'test'
            vbox.customize ['modifyvm', :id, '--memory', 1024]
        end

        # Expose an IP
        test.vm.network :private_network, ip: '14.14.14.14'

        # Install Oxypanel
        test.vm.provision 'shell', path: './deploy/bootstrap.sh'
    end

    # Test device
    config.vm.define :device, autostart: false do |device|
        device.vm.hostname = 'oxypanel-device'
        device.vm.box = 'ubuntu/precise64'
        device.vm.box_url = 'http://files.vagrantup.com/precise64.box'

        device.ssh.private_key_path = './test/insecure_private_key'

        # Expose an IP
        device.vm.network :private_network, ip: '15.15.15.15'
    end
end