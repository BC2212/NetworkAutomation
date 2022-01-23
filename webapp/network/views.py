from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from napalm import get_network_driver
from netmiko import ConnectHandler

from .models import Device

INTERFACE_STATUS_CHANGE_TEMPLATE = """inteface {interface_name}"""

def index(request: HttpRequest) -> HttpResponse:
    devices = Device.objects.all()
    context = {
        'title': 'Network Controller',
        'devices': devices
    }
    return render(request, 'base.html', context)

def get_device_stats(request: HttpRequest, device_id) -> HttpResponse:
    device = Device.objects.get(pk=device_id)
    if request.method == 'GET':
        driver = get_network_driver(device.napalm_driver)
        with driver(device.host, device.username, device.password) as device_conn:
            interfaces = device_conn.get_interfaces()
        context = {
            'device': device,
            'interfaces': interfaces,
        }
        return render(request, 'device.html', context)
    elif request.method == 'POST':
        interface_name = request.POST.get("interface_name")
        enabled_interface = request.POST.get("enable")
        config_commands = [f'interface {interface_name}']
        if enabled_interface == 'False':
            config_commands.append('shutdown')
        else:
            config_commands.append('no shutdown')
        conn_params = {
            'ip': device.host,
            'username': device.username,
            'password': device.password,
            'device_type': device.netmiko_device_type,
        }
        print('begin')
        with ConnectHandler(**conn_params) as device_conn:
            print('end')
            device_conn.send_config_set(config_commands)
        return redirect(f'/device/{device.id}')