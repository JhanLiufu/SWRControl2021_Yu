"""""""""
Written by Mengzhan Liufu and Sameera Shridhar at Yu Lab, the University of Chicago, November 2021
"""""""""

from trodesnetwork import trodes
from trodesnetwork import socket


def call_statescript(hardware, function_num):
    """
    Call a ECU StateScript method of index function_num
    :param hardware: trodes.hardware object
    :param function_num: the index of StateScript funciton defined in Trodes
    :return message: the message sent from trodes (unpacked by msgpack.unpackb) to see if the calling is successful
    """
    message = hardware.ecu_shortcut_message(function_num)
    return message


def connect_to_trodes(local_server_address, count_per_lfp):
    """
    Connect python client to trodes, get hardware sampling rate and calculate lfp sampling rate
    :param local_server_address: the tcp address of trodes server
    :param count_per_lfp: for how many samples one lfp package is sent
    :return: lfp subscriber object, trodes_hardware, trodes_inforequester, lfp sampling rate and lfp sampling period
    :rtype: list [object, object, object, int, int]
    """
    client = subscribe_to_lfp(local_server_address)
    info = get_trodes_info(local_server_address)
    hardware = get_trodes_hardware(local_server_address)
    info = get_trodes_info(local_server_address)
    lfp_sampling_rate = info.request_timerate() / count_per_lfp
    lfp_sampling_period = (1 / lfp_sampling_rate) * (10 ** 9)

    return client, hardware, info, lfp_sampling_rate, lfp_sampling_period


def subscribe_to_lfp(local_server_address):
    """
    Return a trodes.socket subscriber to LFP data

    :param local_server_address: tcp server address of trodes

    :return: channel data
    :rtype: list, each element is of type int corresponding to each data channel
    """
    return socket.SourceSubscriber('source.lfp', server_address=local_server_address)


def get_trodes_info(local_server_address):
    """
    :param local_server_address:

    :return: TrodesInfoRequester Object
    :rtype: object
    """
    return trodes.TrodesInfoRequester(server_address=local_server_address)


def get_trodes_hardware(local_server_address):
    """
    :param local_server_address:

    :return: TrodesHardware Object
    :rtype: object
    """
    return trodes.TrodesHardware(server_address=local_server_address)