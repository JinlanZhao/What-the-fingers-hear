{
    "patcher": {
        "fileversion": 1,
        "appversion": {
            "major": 9,
            "minor": 1,
            "revision": 1,
            "architecture": "x64",
            "modernui": 1
        },
        "classnamespace": "box",
        "rect": [ 460.0, 142.0, 1339.0, 878.0 ],
        "boxes": [
            {
                "box": {
                    "id": "obj-102",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 983.0, 155.0, 177.0, 22.0 ],
                    "text": "stem_player 08_WW_bsn2.wav"
                }
            },
            {
                "box": {
                    "id": "obj-76",
                    "maxclass": "button",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 319.0, 678.0, 24.0, 24.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-74",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 206.5, 679.0, 109.0, 22.0 ],
                    "text": "s~ braille_playgate"
                }
            },
            {
                "box": {
                    "id": "obj-73",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 88.0, 679.0, 112.0, 22.0 ],
                    "text": "s~ braille_playhead"
                }
            },
            {
                "box": {
                    "id": "obj-72",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 3,
                    "outlettype": [ "signal", "signal", "bang" ],
                    "patching_rect": [ 162.0, 640.5, 108.0, 22.0 ],
                    "text": "line~ @activeout 1"
                }
            },
            {
                "box": {
                    "id": "obj-71",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 162.0, 583.0, 59.0, 22.0 ],
                    "text": "$1, $2 $3"
                }
            },
            {
                "box": {
                    "id": "obj-68",
                    "maxclass": "button",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 149.0, 489.0, 24.0, 24.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-62",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [ "", "" ],
                    "patching_rect": [ 162.0, 550.0, 38.0, 22.0 ],
                    "text": "zl reg"
                }
            },
            {
                "box": {
                    "id": "obj-60",
                    "maxclass": "ezdac~",
                    "numinlets": 2,
                    "numoutlets": 0,
                    "patching_rect": [ 691.5, 629.0, 45.0, 45.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-59",
                    "lastchannelcount": 0,
                    "maxclass": "live.gain~",
                    "numinlets": 2,
                    "numoutlets": 5,
                    "outlettype": [ "signal", "signal", "", "float", "list" ],
                    "parameter_enable": 1,
                    "patching_rect": [ 699.0, 469.0, 48.0, 136.0 ],
                    "saved_attribute_attributes": {
                        "valueof": {
                            "parameter_longname": "live.gain~[28]",
                            "parameter_mmax": 6.0,
                            "parameter_mmin": -70.0,
                            "parameter_modmode": 3,
                            "parameter_shortname": "live.gain~[28]",
                            "parameter_type": 0,
                            "parameter_unitstyle": 4
                        }
                    },
                    "varname": "live.gain~"
                }
            },
            {
                "box": {
                    "id": "obj-55",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1178.5, 253.0, 180.0, 22.0 ],
                    "text": "stem_player 29_OTH_stem.wav"
                }
            },
            {
                "box": {
                    "id": "obj-53",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 995.5, 253.0, 181.0, 22.0 ],
                    "text": "stem_player 28_OTH_room.wav"
                }
            },
            {
                "box": {
                    "id": "obj-51",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 816.5, 253.0, 177.0, 22.0 ],
                    "text": "stem_player 27_OTH_riser.wav"
                }
            },
            {
                "box": {
                    "id": "obj-48",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 631.5, 253.0, 183.0, 22.0 ],
                    "text": "stem_player 26_OTH_crash.wav"
                }
            },
            {
                "box": {
                    "id": "obj-46",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1326.0, 229.0, 165.0, 22.0 ],
                    "text": "stem_player 25_STR_cb.wav"
                }
            },
            {
                "box": {
                    "id": "obj-45",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1157.0, 229.0, 165.0, 22.0 ],
                    "text": "stem_player 24_STR_vc.wav"
                }
            },
            {
                "box": {
                    "id": "obj-44",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 987.0, 229.0, 168.0, 22.0 ],
                    "text": "stem_player 23_STR_vla.wav"
                }
            },
            {
                "box": {
                    "id": "obj-43",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 810.0, 229.0, 175.0, 22.0 ],
                    "text": "stem_player 22_STR_vln2.wav"
                }
            },
            {
                "box": {
                    "id": "obj-42",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 633.0, 229.0, 175.0, 22.0 ],
                    "text": "stem_player 21_STR_vln1.wav"
                }
            },
            {
                "box": {
                    "id": "obj-39",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1318.0, 205.0, 167.0, 22.0 ],
                    "text": "stem_player 20_PRC_sn.wav"
                }
            },
            {
                "box": {
                    "id": "obj-38",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1149.0, 205.0, 167.0, 22.0 ],
                    "text": "stem_player 19_PRC_bd.wav"
                }
            },
            {
                "box": {
                    "id": "obj-37",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 978.0, 205.0, 169.0, 22.0 ],
                    "text": "stem_player 18_PRC_glk.wav"
                }
            },
            {
                "box": {
                    "id": "obj-36",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 811.0, 205.0, 163.0, 22.0 ],
                    "text": "stem_player 17_BRS_tb.wav"
                }
            },
            {
                "box": {
                    "id": "obj-34",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 632.0, 205.0, 177.0, 22.0 ],
                    "text": "stem_player 16_BRS_tbn2.wav"
                }
            },
            {
                "box": {
                    "id": "obj-33",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1313.0, 179.0, 177.0, 22.0 ],
                    "text": "stem_player 15_BRS_tbn1.wav"
                }
            },
            {
                "box": {
                    "id": "obj-32",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1137.0, 179.0, 173.0, 22.0 ],
                    "text": "stem_player 14_BRS_tpt2.wav"
                }
            },
            {
                "box": {
                    "id": "obj-30",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 958.0, 179.0, 173.0, 22.0 ],
                    "text": "stem_player 13_BRS_tpt1.wav"
                }
            },
            {
                "box": {
                    "id": "obj-28",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 782.0, 179.0, 170.0, 22.0 ],
                    "text": "stem_player 12_BRS_fh4.wav"
                }
            },
            {
                "box": {
                    "id": "obj-26",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 632.0, 179.0, 144.0, 22.0 ],
                    "text": "stem_player 11_BRS_fh3"
                }
            },
            {
                "box": {
                    "id": "obj-24",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1339.0, 155.0, 170.0, 22.0 ],
                    "text": "stem_player 10_BRS_fh2.wav"
                }
            },
            {
                "box": {
                    "id": "obj-21",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1168.0, 155.0, 170.0, 22.0 ],
                    "text": "stem_player 09_BRS_fh1.wav"
                }
            },
            {
                "box": {
                    "id": "obj-20",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 800.0, 155.0, 177.0, 22.0 ],
                    "text": "stem_player 07_WW_bsn1.wav"
                }
            },
            {
                "box": {
                    "id": "obj-18",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 630.5, 155.0, 167.0, 22.0 ],
                    "text": "stem_player 06_WW_cl2.wav"
                }
            },
            {
                "box": {
                    "id": "obj-16",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1318.0, 129.0, 167.0, 22.0 ],
                    "text": "stem_player 05_WW_cl1.wav"
                }
            },
            {
                "box": {
                    "id": "obj-14",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1145.0, 129.0, 171.0, 22.0 ],
                    "text": "stem_player 04_WW_ob2.wav"
                }
            },
            {
                "box": {
                    "id": "obj-12",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 970.0, 129.0, 171.0, 22.0 ],
                    "text": "stem_player 03_WW_ob1.wav"
                }
            },
            {
                "box": {
                    "id": "obj-8",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 800.0, 129.0, 164.0, 22.0 ],
                    "text": "stem_player 02_WW_fl2.wav"
                }
            },
            {
                "box": {
                    "id": "obj-7",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "signal" ],
                    "patching_rect": [ 753.0, 416.0, 114.0, 22.0 ],
                    "text": "r~ braille_master_R"
                }
            },
            {
                "box": {
                    "id": "obj-6",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "signal" ],
                    "patching_rect": [ 631.5, 416.0, 112.0, 22.0 ],
                    "text": "r~ braille_master_L"
                }
            },
            {
                "box": {
                    "id": "obj-70",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 632.0, 129.0, 164.0, 22.0 ],
                    "text": "stem_player 01_WW_fl1.wav"
                }
            },
            {
                "box": {
                    "id": "obj-63",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 279.0, 583.0, 49.0, 22.0 ],
                    "text": "resume"
                }
            },
            {
                "box": {
                    "id": "obj-61",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 229.0, 583.0, 41.0, 22.0 ],
                    "text": "pause"
                }
            },
            {
                "box": {
                    "id": "obj-54",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 113.0, 583.0, 31.0, 22.0 ],
                    "text": "stop"
                }
            },
            {
                "box": {
                    "id": "obj-49",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 254.0, 491.0, 163.0, 20.0 ],
                    "text": "start time, end time, duration"
                }
            },
            {
                "box": {
                    "id": "obj-47",
                    "maxclass": "newobj",
                    "numinlets": 3,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 181.0, 490.0, 68.0, 22.0 ],
                    "text": "pak 0. 0. 0."
                }
            },
            {
                "box": {
                    "id": "obj-41",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 205.5, 346.0, 55.0, 22.0 ],
                    "text": "pak 0. 0."
                }
            },
            {
                "box": {
                    "id": "obj-35",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 289.5, 444.0, 186.0, 20.0 ],
                    "text": "End Time: Start Time + Duration"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-31",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 205.5, 443.0, 82.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-29",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 205.5, 398.0, 82.0, 22.0 ],
                    "text": "expr $f1 + $f2"
                }
            },
            {
                "box": {
                    "id": "obj-27",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 451.0, 130.0, 114.0, 20.0 ],
                    "text": "number of bars"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-25",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 397.0, 239.0, 85.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-23",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 397.0, 188.0, 67.0, 22.0 ],
                    "text": "* 1666.667"
                }
            },
            {
                "box": {
                    "id": "obj-22",
                    "maxclass": "number",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 397.0, 129.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-19",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 99.0, 129.0, 59.0, 20.0 ],
                    "text": "start bar"
                }
            },
            {
                "box": {
                    "id": "obj-17",
                    "linecount": 3,
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 11.0, 11.0, 150.0, 47.0 ],
                    "text": "144 BPM\n4/4\n16 Bars"
                }
            },
            {
                "box": {
                    "id": "obj-15",
                    "linecount": 3,
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 119.0, 196.0, 237.0, 47.0 ],
                    "text": "1 beat = 60 / 144 = 0.416667 sec\n1 bar = 0.416667 × 4 = 1.666667 sec\n1 bar = 1666.667 ms"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-13",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 44.0, 253.0, 93.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-11",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 44.0, 215.0, 67.0, 22.0 ],
                    "text": "* 1666.667"
                }
            },
            {
                "box": {
                    "id": "obj-10",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "int" ],
                    "patching_rect": [ 44.0, 172.0, 29.5, 22.0 ],
                    "text": "- 1"
                }
            },
            {
                "box": {
                    "id": "obj-9",
                    "maxclass": "number",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 44.0, 128.0, 50.0, 22.0 ]
                }
            }
        ],
        "lines": [
            {
                "patchline": {
                    "destination": [ "obj-11", 0 ],
                    "source": [ "obj-10", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-13", 0 ],
                    "source": [ "obj-11", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-41", 0 ],
                    "order": 0,
                    "source": [ "obj-13", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-47", 0 ],
                    "order": 1,
                    "source": [ "obj-13", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-23", 0 ],
                    "source": [ "obj-22", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-25", 0 ],
                    "source": [ "obj-23", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-41", 1 ],
                    "order": 0,
                    "source": [ "obj-25", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-47", 2 ],
                    "order": 1,
                    "source": [ "obj-25", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-31", 0 ],
                    "source": [ "obj-29", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-47", 1 ],
                    "source": [ "obj-31", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-29", 0 ],
                    "source": [ "obj-41", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-62", 1 ],
                    "source": [ "obj-47", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-72", 0 ],
                    "source": [ "obj-54", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-60", 1 ],
                    "source": [ "obj-59", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-60", 0 ],
                    "source": [ "obj-59", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-59", 0 ],
                    "source": [ "obj-6", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-72", 0 ],
                    "source": [ "obj-61", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-71", 0 ],
                    "source": [ "obj-62", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-72", 0 ],
                    "source": [ "obj-63", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-62", 0 ],
                    "source": [ "obj-68", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-59", 1 ],
                    "source": [ "obj-7", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-72", 0 ],
                    "source": [ "obj-71", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-73", 0 ],
                    "source": [ "obj-72", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-74", 0 ],
                    "source": [ "obj-72", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-76", 0 ],
                    "source": [ "obj-72", 2 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-10", 0 ],
                    "source": [ "obj-9", 0 ]
                }
            }
        ],
        "parameters": {
            "obj-102::obj-7": [ "live.gain~[16]", "live.gain~", 0 ],
            "obj-12::obj-7": [ "live.gain~[31]", "live.gain~", 0 ],
            "obj-14::obj-7": [ "live.gain~[32]", "live.gain~", 0 ],
            "obj-16::obj-7": [ "live.gain~[33]", "live.gain~", 0 ],
            "obj-18::obj-7": [ "live.gain~[34]", "live.gain~", 0 ],
            "obj-20::obj-7": [ "live.gain~[35]", "live.gain~", 0 ],
            "obj-21::obj-7": [ "live.gain~[36]", "live.gain~", 0 ],
            "obj-24::obj-7": [ "live.gain~[37]", "live.gain~", 0 ],
            "obj-26::obj-7": [ "live.gain~[38]", "live.gain~", 0 ],
            "obj-28::obj-7": [ "live.gain~[39]", "live.gain~", 0 ],
            "obj-30::obj-7": [ "live.gain~[40]", "live.gain~", 0 ],
            "obj-32::obj-7": [ "live.gain~[41]", "live.gain~", 0 ],
            "obj-33::obj-7": [ "live.gain~[42]", "live.gain~", 0 ],
            "obj-34::obj-7": [ "live.gain~[2]", "live.gain~", 0 ],
            "obj-36::obj-7": [ "live.gain~[3]", "live.gain~", 0 ],
            "obj-37::obj-7": [ "live.gain~[4]", "live.gain~", 0 ],
            "obj-38::obj-7": [ "live.gain~[5]", "live.gain~", 0 ],
            "obj-39::obj-7": [ "live.gain~[6]", "live.gain~", 0 ],
            "obj-42::obj-7": [ "live.gain~[7]", "live.gain~", 0 ],
            "obj-43::obj-7": [ "live.gain~[8]", "live.gain~", 0 ],
            "obj-44::obj-7": [ "live.gain~[9]", "live.gain~", 0 ],
            "obj-45::obj-7": [ "live.gain~[10]", "live.gain~", 0 ],
            "obj-46::obj-7": [ "live.gain~[11]", "live.gain~", 0 ],
            "obj-48::obj-7": [ "live.gain~[12]", "live.gain~", 0 ],
            "obj-51::obj-7": [ "live.gain~[13]", "live.gain~", 0 ],
            "obj-53::obj-7": [ "live.gain~[14]", "live.gain~", 0 ],
            "obj-55::obj-7": [ "live.gain~[15]", "live.gain~", 0 ],
            "obj-59": [ "live.gain~[28]", "live.gain~[28]", 0 ],
            "obj-70::obj-7": [ "live.gain~[30]", "live.gain~", 0 ],
            "obj-8::obj-7": [ "live.gain~[1]", "live.gain~", 0 ],
            "parameter_overrides": {
                "obj-102::obj-7": {
                    "parameter_longname": "live.gain~[16]"
                },
                "obj-12::obj-7": {
                    "parameter_longname": "live.gain~[31]"
                },
                "obj-14::obj-7": {
                    "parameter_longname": "live.gain~[32]"
                },
                "obj-16::obj-7": {
                    "parameter_longname": "live.gain~[33]"
                },
                "obj-18::obj-7": {
                    "parameter_longname": "live.gain~[34]"
                },
                "obj-20::obj-7": {
                    "parameter_longname": "live.gain~[35]"
                },
                "obj-21::obj-7": {
                    "parameter_longname": "live.gain~[36]"
                },
                "obj-24::obj-7": {
                    "parameter_longname": "live.gain~[37]"
                },
                "obj-26::obj-7": {
                    "parameter_longname": "live.gain~[38]"
                },
                "obj-28::obj-7": {
                    "parameter_longname": "live.gain~[39]"
                },
                "obj-30::obj-7": {
                    "parameter_longname": "live.gain~[40]"
                },
                "obj-32::obj-7": {
                    "parameter_longname": "live.gain~[41]"
                },
                "obj-33::obj-7": {
                    "parameter_longname": "live.gain~[42]"
                },
                "obj-34::obj-7": {
                    "parameter_longname": "live.gain~[2]"
                },
                "obj-36::obj-7": {
                    "parameter_longname": "live.gain~[3]"
                },
                "obj-37::obj-7": {
                    "parameter_longname": "live.gain~[4]"
                },
                "obj-38::obj-7": {
                    "parameter_longname": "live.gain~[5]"
                },
                "obj-39::obj-7": {
                    "parameter_longname": "live.gain~[6]"
                },
                "obj-42::obj-7": {
                    "parameter_longname": "live.gain~[7]"
                },
                "obj-43::obj-7": {
                    "parameter_longname": "live.gain~[8]"
                },
                "obj-44::obj-7": {
                    "parameter_longname": "live.gain~[9]"
                },
                "obj-45::obj-7": {
                    "parameter_longname": "live.gain~[10]"
                },
                "obj-46::obj-7": {
                    "parameter_longname": "live.gain~[11]"
                },
                "obj-48::obj-7": {
                    "parameter_longname": "live.gain~[12]"
                },
                "obj-51::obj-7": {
                    "parameter_longname": "live.gain~[13]"
                },
                "obj-53::obj-7": {
                    "parameter_longname": "live.gain~[14]"
                },
                "obj-55::obj-7": {
                    "parameter_longname": "live.gain~[15]"
                },
                "obj-70::obj-7": {
                    "parameter_longname": "live.gain~[30]"
                }
            },
            "inherited_shortname": 1
        },
        "autosave": 0,
        "toolbaradditions": [ "Data Knot" ]
    }
}