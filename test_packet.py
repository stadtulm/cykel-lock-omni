# import binascii
import datetime
import unittest

from packet import Packet, Response


class PacketTestCase(unittest.TestCase):
    def pparse(self, packet, instance=None):
        pp = instance or Packet()
        parsed = pp.parse(packet)
        # print(binascii.hexlify(packet))
        # print(parsed)
        return parsed

    def test_signin_packet(self):
        packet = b"*CMDR,OM,863725031194523,000000000000,Q0,410#"
        parsed = self.pparse(packet)
        self.assertEqual(parsed.devicecode, "OM")
        self.assertEqual(parsed.imei, "863725031194523")
        self.assertEqual(parsed.datetime, None)
        self.assertEqual(parsed.cmd, "signin")
        self.assertEqual(parsed.data.voltage, 4.10)

    def test_heartbeat_packet(self):
        packet = b"*CMDR,OM,863725031194523,161201150000,H0,1,400,24#"
        parsed = self.pparse(packet)
        self.assertEqual(parsed.devicecode, "OM")
        self.assertEqual(parsed.imei, "863725031194523")
        self.assertEqual(parsed.datetime, datetime.datetime(2016, 12, 1, 15, 0))
        self.assertEqual(parsed.cmd, "heartbeat")
        self.assertEqual(parsed.data.locked, True)
        self.assertEqual(parsed.data.voltage, 4.00)
        self.assertEqual(parsed.data.gsmsignal, 24)

    def test_lock_packet(self):
        packet = b"*CMDR,OM,863725031194523,000000000000,L1,1,1497689816,20#"
        parsed = self.pparse(packet)
        self.assertEqual(parsed.devicecode, "OM")
        self.assertEqual(parsed.imei, "863725031194523")
        self.assertEqual(parsed.datetime, None)
        self.assertEqual(parsed.cmd, "lock")
        self.assertEqual(parsed.data.userid, b"1")
        self.assertEqual(parsed.data.unlocked_at, b"1497689816")
        self.assertEqual(parsed.data.riding_time, b"20")

    def test_update_packet(self):
        packet = b"*CMDR,OM,863725031194523,000000000000,U0,68,A1,Mar 13 2020#"
        parsed = self.pparse(packet)
        self.assertEqual(parsed.devicecode, "OM")
        self.assertEqual(parsed.imei, "863725031194523")
        self.assertEqual(parsed.datetime, None)
        self.assertEqual(parsed.cmd, "update")

    def test_invalid_position_packet(self):
        packet = (
            b"*CMDR,OM,863725031194523,000000000000,D0,0,140516.00,V,,,,,,,180121,,,N#"
        )
        parsed = self.pparse(packet)
        self.assertEqual(parsed.devicecode, "OM")
        self.assertEqual(parsed.imei, "863725031194523")
        self.assertEqual(parsed.datetime, None)
        self.assertEqual(parsed.cmd, "position")
        self.assertEqual(parsed.data.time, b"140516.00")
        self.assertEqual(parsed.data.status, "invalid")
        self.assertEqual(parsed.data.lat, None)
        self.assertEqual(parsed.data.lat_h, "invalid")
        self.assertEqual(parsed.data.lon, None)
        self.assertEqual(parsed.data.lon_h, "invalid")
        self.assertEqual(parsed.data.ground_rate, None)
        self.assertEqual(parsed.data.heading, None)
        self.assertEqual(parsed.data.date, b"180121")
        self.assertEqual(parsed.data.mag_degrees, None)
        self.assertEqual(parsed.data.mag_direction, None)
        self.assertEqual(parsed.data.mode, "invalid")

    def test_position_packet(self):
        packet = (
            b"*CMDR,OM,863725031194523,000000000000,D0,0,205719.00,A,4824.07609,N,00959.40370,E,05,2.02,200121,494.6,M,A#"
        )
        parsed = self.pparse(packet)
        self.assertEqual(parsed.devicecode, "OM")
        self.assertEqual(parsed.imei, "863725031194523")
        self.assertEqual(parsed.datetime, None)
        self.assertEqual(parsed.cmd, "position")
        self.assertEqual(parsed.data.time, b"205719.00")
        self.assertEqual(parsed.data.status, "active")
        self.assertEqual(parsed.data.lat, b"4824.07609")
        self.assertEqual(parsed.data.lat_h, "north")
        self.assertEqual(parsed.data.lon, b"00959.40370")
        self.assertEqual(parsed.data.lon_h, "east")
        self.assertEqual(parsed.data.ground_rate, b"05")
        self.assertEqual(parsed.data.heading, b"2.02")
        self.assertEqual(parsed.data.date, b"200121")
        self.assertEqual(parsed.data.mag_degrees, b"494.6")
        self.assertEqual(parsed.data.mag_direction, b"M")
        self.assertEqual(parsed.data.mode, "automatic")


class ResponseTestCase(unittest.TestCase):
    def test_lock_response_packet(self):
        pp = Response()
        packet = pp.build(
            dict(
                devicecode="OM",
                imei="863725031194523",
                datetime=datetime.datetime(2016, 12, 1, 15, 0),
                data="L1",
            )
        )
        self.assertEqual(
            packet, b"\xff\xff*CMDS,OM,863725031194523,161201150000,Re,L1#"
        )
