#!/usr/bin/env python

# Test whether a retained PUBLISH to a topic with QoS 0 is sent with
# retain=false to an already subscribed client.

import inspect, os, sys
# From http://stackoverflow.com/questions/279237/python-import-a-module-from-a-folder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"..")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import mosq_test

rc = 1
keepalive = 60
mid = 16
connect_packet = mosq_test.gen_connect("retain-qos0-fresh-test", keepalive=keepalive)
connack_packet = mosq_test.gen_connack(rc=0)

publish_packet = mosq_test.gen_publish("retain/qos0/test", qos=0, payload="retained message", retain=True)
publish_fresh_packet = mosq_test.gen_publish("retain/qos0/test", qos=0, payload="retained message")
subscribe_packet = mosq_test.gen_subscribe(mid, "retain/qos0/test", 0)
suback_packet = mosq_test.gen_suback(mid, 0)

cmd = ['../../src/mosquitto', '-p', '1888']
broker = mosq_test.start_broker(filename=os.path.basename(__file__), cmd=cmd)

try:
    sock = mosq_test.do_client_connect(connect_packet, connack_packet)
    sock.send(subscribe_packet)

    if mosq_test.expect_packet(sock, "suback", suback_packet):
        sock.send(publish_packet)

        if mosq_test.expect_packet(sock, "publish", publish_fresh_packet):
            rc = 0
    sock.close()
finally:
    broker.terminate()
    broker.wait()
    if rc:
        (stdo, stde) = broker.communicate()
        print(stde)

exit(rc)

