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
        "rect": [ 34.0, 96.0, 1660.0, 987.0 ],
        "boxes": [
            {
                "box": {
                    "id": "obj-115",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 773.0, 226.0, 39.0, 20.0 ],
                    "text": "FULL"
                }
            },
            {
                "box": {
                    "id": "obj-113",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 1216.0, 640.0, 42.0, 20.0 ],
                    "text": "STEM"
                }
            },
            {
                "box": {
                    "id": "obj-108",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "bang", "bang" ],
                    "patching_rect": [ 743.0, 263.0, 32.0, 22.0 ],
                    "text": "t b b"
                }
            },
            {
                "box": {
                    "id": "obj-104",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 273.0, 670.0, 67.0, 22.0 ],
                    "text": "seek $1 $2"
                }
            },
            {
                "box": {
                    "id": "obj-86",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [ "", "" ],
                    "patching_rect": [ 208.0, 670.0, 50.0, 22.0 ],
                    "text": "zl reg"
                }
            },
            {
                "box": {
                    "id": "obj-112",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "int" ],
                    "patching_rect": [ 204.0, 194.0, 29.5, 22.0 ],
                    "text": "i"
                }
            },
            {
                "box": {
                    "id": "obj-111",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 243.0, 194.0, 75.0, 22.0 ],
                    "text": "expr 17 - $i1"
                }
            },
            {
                "box": {
                    "id": "obj-110",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [ "bang", "int", "int" ],
                    "patching_rect": [ 217.0, 152.0, 45.0, 22.0 ],
                    "text": "t b i i"
                }
            },
            {
                "box": {
                    "id": "obj-107",
                    "maxclass": "number",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 247.0, 106.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-101",
                    "maxclass": "newobj",
                    "numinlets": 3,
                    "numoutlets": 3,
                    "outlettype": [ "", "", "" ],
                    "patching_rect": [ 247.0, 61.0, 139.0, 22.0 ],
                    "text": "route /bar /stop"
                }
            },
            {
                "box": {
                    "id": "obj-90",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 173.0, 61.0, 61.0, 22.0 ],
                    "text": "print OSC"
                }
            },
            {
                "box": {
                    "id": "obj-75",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 221.0, 19.0, 97.0, 22.0 ],
                    "text": "udpreceive 7400"
                }
            },
            {
                "box": {
                    "id": "obj-85",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [ "bang", "bang", "bang" ],
                    "patching_rect": [ 1261.5, 689.0, 42.0, 22.0 ],
                    "text": "t b b b"
                }
            },
            {
                "box": {
                    "id": "obj-83",
                    "maxclass": "button",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 1262.0, 638.0, 24.0, 24.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-79",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 1334.0, 741.0, 51.0, 22.0 ],
                    "text": "all 0."
                }
            },
            {
                "box": {
                    "id": "obj-106",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 1273.0, 741.0, 37.0, 22.0 ],
                    "text": "vla 1."
                }
            },
            {
                "box": {
                    "id": "obj-105",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 1204.0, 741.0, 44.0, 22.0 ],
                    "text": "vln1 0."
                }
            },
            {
                "box": {
                    "id": "obj-103",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 1204.0, 807.0, 112.0, 22.0 ],
                    "text": "s braille_track_gain"
                }
            },
            {
                "box": {
                    "fontface": 1,
                    "id": "obj-99",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 1483.0, 535.0, 163.0, 20.0 ],
                    "text": "Others",
                    "textjustification": 1
                }
            },
            {
                "box": {
                    "fontface": 1,
                    "id": "obj-97",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 1363.0, 341.0, 163.0, 20.0 ],
                    "text": "Strings",
                    "textjustification": 1
                }
            },
            {
                "box": {
                    "fontface": 1,
                    "id": "obj-95",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 1601.0, 360.0, 163.0, 20.0 ],
                    "text": "Percussion",
                    "textjustification": 1
                }
            },
            {
                "box": {
                    "fontface": 1,
                    "id": "obj-93",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 1599.0, 48.0, 163.0, 20.0 ],
                    "text": "Brass",
                    "textjustification": 1
                }
            },
            {
                "box": {
                    "fontface": 1,
                    "id": "obj-91",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 1363.0, 48.0, 163.0, 20.0 ],
                    "text": "Woodwinds",
                    "textjustification": 1
                }
            },
            {
                "box": {
                    "id": "obj-88",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 1042.0, 902.0, 69.0, 20.0 ],
                    "text": "dry signal"
                }
            },
            {
                "box": {
                    "id": "obj-87",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 715.0, 902.0, 69.0, 20.0 ],
                    "text": "wet signal"
                }
            },
            {
                "box": {
                    "appearance": 3,
                    "id": "obj-84",
                    "maxclass": "live.dial",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "float" ],
                    "parameter_enable": 1,
                    "patching_rect": [ 434.0, 772.0, 50.0, 63.0 ],
                    "saved_attribute_attributes": {
                        "valueof": {
                            "parameter_longname": "Mix[1]",
                            "parameter_mmax": 1.0,
                            "parameter_modmode": 3,
                            "parameter_shortname": "MIx",
                            "parameter_type": 0,
                            "parameter_unitstyle": 1
                        }
                    },
                    "varname": "Reverb_Mix[1]"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-80",
                    "maxclass": "flonum",
                    "maximum": 1.0,
                    "minimum": 0.0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 1,
                    "patching_rect": [ 601.0, 818.0, 50.0, 22.0 ],
                    "saved_attribute_attributes": {
                        "valueof": {
                            "parameter_longname": "mix_R",
                            "parameter_mmax": 1.0,
                            "parameter_modmode": 3,
                            "parameter_shortname": "mix_R",
                            "parameter_type": 0
                        }
                    },
                    "varname": "reverbMix_R"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-77",
                    "maxclass": "flonum",
                    "maximum": 1.0,
                    "minimum": 0.0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 1,
                    "patching_rect": [ 512.0, 818.0, 50.0, 22.0 ],
                    "saved_attribute_attributes": {
                        "valueof": {
                            "parameter_invisible": 1,
                            "parameter_longname": "mix_L",
                            "parameter_mmax": 1.0,
                            "parameter_modmode": 0,
                            "parameter_shortname": "mix_L",
                            "parameter_type": 3
                        }
                    },
                    "varname": "reverbMix_L"
                }
            },
            {
                "box": {
                    "id": "obj-69",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "signal" ],
                    "patching_rect": [ 591.0, 858.0, 29.5, 22.0 ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-56",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "signal" ],
                    "patching_rect": [ 502.0, 858.0, 29.5, 22.0 ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-40",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 914.0, 901.0, 116.0, 22.0 ],
                    "text": "s~ braille_master_R"
                }
            },
            {
                "box": {
                    "id": "obj-52",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 791.0, 901.0, 114.0, 22.0 ],
                    "text": "s~ braille_master_L"
                }
            },
            {
                "box": {
                    "id": "obj-2",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "signal" ],
                    "patching_rect": [ 914.0, 844.0, 103.0, 22.0 ],
                    "text": "r~ braille_stem_R"
                }
            },
            {
                "box": {
                    "id": "obj-4",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "signal" ],
                    "patching_rect": [ 791.0, 844.0, 101.0, 22.0 ],
                    "text": "r~ braille_stem_L"
                }
            },
            {
                "box": {
                    "autosave": 1,
                    "bgmode": 0,
                    "border": 0,
                    "clickthrough": 0,
                    "id": "obj-81",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 8,
                    "offset": [ 0.0, 0.0 ],
                    "outlettype": [ "signal", "signal", "", "list", "int", "", "", "" ],
                    "patching_rect": [ 502.0, 504.0, 327.0, 292.0 ],
                    "save": [ "#N", "vst~", "loaduniqueid", 0, "C74_AU:/ValhallaVintageVerb", ";" ],
                    "saved_attribute_attributes": {
                        "valueof": {
                            "parameter_invisible": 1,
                            "parameter_longname": "vst~",
                            "parameter_modmode": 0,
                            "parameter_shortname": "vst~",
                            "parameter_type": 3
                        }
                    },
                    "saved_object_attributes": {
                        "parameter_enable": 1,
                        "parameter_mappable": 0
                    },
                    "snapshot": {
                        "filetype": "C74Snapshot",
                        "version": 2,
                        "minorversion": 0,
                        "name": "snapshotlist",
                        "origin": "vst~",
                        "type": "list",
                        "subtype": "Undefined",
                        "embed": 1,
                        "snapshot": {
                            "pluginname": "ValhallaVintageVerb.auinfo",
                            "plugindisplayname": "ValhallaVintageVerb",
                            "pluginsavedname": "",
                            "pluginsaveduniqueid": 2018798117,
                            "version": 1,
                            "isbank": 0,
                            "isbase64": 1,
                            "sliderorder": [],
                            "slidervisibility": [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
                            "blob": "986.hAGaoMGcv.C1AHv.DTfAGfPBJrvDTTgEWvUag4VclE1XzUmbkIGUjEFcgwUYrUVak4Fcs3VXsU1UyUmXzkGbkckckI2bo8laTQWdvU1WP7fZ0MVYPwVcmklaSQWXzUFUtEVakIwaDklaOAAk..............PD....v7Cf......PL9.H......HiOWmjL....y7Cf.......M+........TyOe7Gd....13y3u1M...vM.........fyO........47Cf.....XvG+.H.....F.hO6gUb..fAg3ivOxE..XfH+bQKNB..FLB.......fAj3ipptJ..XPI8nhpqJMCM3PDQESTxD8CPDELUkjavUGcQ+fDV8TczAWczIgckU1LP.fDgUmY38TDBLkUCISHJI...vyO30FafXWYxMWZu4VOhDiKvHBHk41XuQVZtcVOhTEUF0BNh7iOfviUgwFZgwFagYUZtQWXmUlUkImXf.Ga0cVZtYUYxMWZu4VOhHiKw3hLh.BbxU1bkQmSg0VY8HBQkYVX0wFch.RSogWOhDiKvHBHPIWYDUFagkWOh.iKyPCLxLCMyXSNvLSN0LSM0HBHDU1XgkWOh.iKxTSNvfiLvDSNyHSNvbSLh.xTooWY8HBLtPCMyfCM2XSM1HSMh.RPzQWXisVOh.iK0HBHBE1by0TcrQWOh.iK1HyLvLCN2XCN2XCNyDCL0HBHBE1byg0a1Ulb8HBLtPCMzbCLwDCL0LSM1HSL1PiHffTZmg1TnUFal0iHv3BLh.BRocFZFIWYw0iHv3BNxLSM3LSN1.SMyLSLzHSLh.RQgIGa4QTZlYVcyk1at0iHv3hMzXSL4DCMwfSL2.SNxjiHfvTXzUFQoYlY0MWZu4VOhDiKvHBHM8FYREFck0iHv3hLzTCM0PSM1PiM4.SM3jSNh.RSuQFQkAGcn0iHv3xL2jSN4jSN4TiLyDiMxfCMh.BRocFZCUGc8HBLtfCL1PSNzDSL1bCNyDCMxDiHfvza2MTcz0iHv3RLxTSNxbyMyDyL4PyM1bCNh.xPuw1ax0zajUVOh.iKyLyLyLyLyPyLxXyMzPCL3HBHRUlckImXM8FYk0iHv3BLzDiM1XiM1bSNvfCMy.SLh.RaogGSuM1Z8HBLh.RcocUZjQGZ8HRNyTiHfTWZHUVZmgFc8HBMyTiHu3C.XUkazkFcrUFY.f..Y.fI.rB.3..P.fD.MAvW.PF.oE..ATP.GDPBAvP.ND.EAbQ.dDvHATR.pLPf........BD..........X...................CnH"
                        },
                        "snapshotlist": {
                            "current_snapshot": 0,
                            "entries": [
                                {
                                    "filetype": "C74Snapshot",
                                    "version": 2,
                                    "minorversion": 0,
                                    "name": "ValhallaVintageVerb",
                                    "origin": "ValhallaVintageVerb.auinfo",
                                    "type": "AudioUnit",
                                    "subtype": "AudioEffect",
                                    "embed": 0,
                                    "snapshot": {
                                        "pluginname": "ValhallaVintageVerb.auinfo",
                                        "plugindisplayname": "ValhallaVintageVerb",
                                        "pluginsavedname": "",
                                        "pluginsaveduniqueid": 2018798117,
                                        "version": 1,
                                        "isbank": 0,
                                        "isbase64": 1,
                                        "sliderorder": [],
                                        "slidervisibility": [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
                                        "blob": "986.hAGaoMGcv.C1AHv.DTfAGfPBJrvDTTgEWvUag4VclE1XzUmbkIGUjEFcgwUYrUVak4Fcs3VXsU1UyUmXzkGbkckckI2bo8laTQWdvU1WP7fZ0MVYPwVcmklaSQWXzUFUtEVakIwaDklaOAAk..............PD....v7Cf......PL9.H......HiOWmjL....y7Cf.......M+........TyOe7Gd....13y3u1M...vM.........fyO........47Cf.....XvG+.H.....F.hO6gUb..fAg3ivOxE..XfH+bQKNB..FLB.......fAj3ipptJ..XPI8nhpqJMCM3PDQESTxD8CPDELUkjavUGcQ+fDV8TczAWczIgckU1LP.fDgUmY38TDBLkUCISHJI...vyO30FafXWYxMWZu4VOhDiKvHBHk41XuQVZtcVOhTEUF0BNh7iOfviUgwFZgwFagYUZtQWXmUlUkImXf.Ga0cVZtYUYxMWZu4VOhHiKw3hLh.BbxU1bkQmSg0VY8HBQkYVX0wFch.RSogWOhDiKvHBHPIWYDUFagkWOh.iKyPCLxLCMyXSNvLSN0LSM0HBHDU1XgkWOh.iKxTSNvfiLvDSNyHSNvbSLh.xTooWY8HBLtPCMyfCM2XSM1HSMh.RPzQWXisVOh.iK0HBHBE1by0TcrQWOh.iK1HyLvLCN2XCN2XCNyDCL0HBHBE1byg0a1Ulb8HBLtPCMzbCLwDCL0LSM1HSL1PiHffTZmg1TnUFal0iHv3BLh.BRocFZFIWYw0iHv3BNxLSM3LSN1.SMyLSLzHSLh.RQgIGa4QTZlYVcyk1at0iHv3hMzXSL4DCMwfSL2.SNxjiHfvTXzUFQoYlY0MWZu4VOhDiKvHBHM8FYREFck0iHv3hLzTCM0PSM1PiM4.SM3jSNh.RSuQFQkAGcn0iHv3xL2jSN4jSN4TiLyDiMxfCMh.BRocFZCUGc8HBLtfCL1PSNzDSL1bCNyDCMxDiHfvza2MTcz0iHv3RLxTSNxbyMyDyL4PyM1bCNh.xPuw1ax0zajUVOh.iKyLyLyLyLyPyLxXyMzPCL3HBHRUlckImXM8FYk0iHv3BLzDiM1XiM1bSNvfCMy.SLh.RaogGSuM1Z8HBLh.RcocUZjQGZ8HRNyTiHfTWZHUVZmgFc8HBMyTiHu3C.XUkazkFcrUFY.f..Y.fI.rB.3..P.fD.MAvW.PF.oE..ATP.GDPBAvP.ND.EAbQ.dDvHATR.pLPf........BD..........X...................CnH"
                                    },
                                    "fileref": {
                                        "name": "ValhallaVintageVerb",
                                        "filename": "ValhallaVintageVerb_20260914.maxsnap",
                                        "filepath": "~/Documents/Max 9/Snapshots",
                                        "filepos": -1,
                                        "snapshotfileid": "9c4cbfdbe60bd0b34f533e65af5f78f8"
                                    }
                                },
                                {
                                    "filetype": "C74Snapshot",
                                    "version": 2,
                                    "minorversion": 0,
                                    "name": "ValhallaVintageVerb[1]",
                                    "origin": "ValhallaVintageVerb.auinfo",
                                    "type": "AudioUnit",
                                    "subtype": "AudioEffect",
                                    "embed": 0,
                                    "snapshot": {
                                        "pluginname": "ValhallaVintageVerb.auinfo",
                                        "plugindisplayname": "ValhallaVintageVerb",
                                        "pluginsavedname": "",
                                        "pluginsaveduniqueid": 2018798117,
                                        "version": 1,
                                        "isbank": 0,
                                        "isbase64": 1,
                                        "sliderorder": [],
                                        "slidervisibility": [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
                                        "blob": "986.hAGaoMGcv.C1AHv.DTfAGfPBJrvDTTgEWvUag4VclE1XzUmbkIGUjEFcgwUYrUVak4Fcs3VXsU1UyUmXzkGbkckckI2bo8laTQWdvU1WP7fZ0MVYPwVcmklaSQWXzUFUtEVakIwaDklaOAAk..............PD....v7Cf......PL9.H......HiOWmjL....y7Cf.......M+........TyOe7Gd....13y3u1M...vM.........fyO........47Cf.....XvG+.H.....F.hO6gUb..fAg3ivOxE..XfH+bQKNB..FLB.......fAj3ipptJ..XPI8nhpqJMCM3PDQESTxD8CPDELUkjavUGcQ+fDV8TczAWczIgckU1LP.fDgUmY38TDBLkUCISHJI...vyO30FafXWYxMWZu4VOhDiKvHBHk41XuQVZtcVOhTEUF0BNh7iOfviUgwFZgwFagYUZtQWXmUlUkImXf.Ga0cVZtYUYxMWZu4VOhHiKw3hLh.BbxU1bkQmSg0VY8HBQkYVX0wFch.RSogWOhDiKvHBHPIWYDUFagkWOh.iKyPCLxLCMyXSNvLSN0LSM0HBHDU1XgkWOh.iKxTSNvfiLvDSNyHSNvbSLh.xTooWY8HBLtPCMyfCM2XSM1HSMh.RPzQWXisVOh.iK0HBHBE1by0TcrQWOh.iK1HyLvLCN2XCN2XCNyDCL0HBHBE1byg0a1Ulb8HBLtPCMzbCLwDCL0LSM1HSL1PiHffTZmg1TnUFal0iHv3BLh.BRocFZFIWYw0iHv3BNxLSM3LSN1.SMyLSLzHSLh.RQgIGa4QTZlYVcyk1at0iHv3hMzXSL4DCMwfSL2.SNxjiHfvTXzUFQoYlY0MWZu4VOhDiKvHBHM8FYREFck0iHv3hLzTCM0PSM1PiM4.SM3jSNh.RSuQFQkAGcn0iHv3xL2jSN4jSN4TiLyDiMxfCMh.BRocFZCUGc8HBLtfCL1PSNzDSL1bCNyDCMxDiHfvza2MTcz0iHv3RLxTSNxbyMyDyL4PyM1bCNh.xPuw1ax0zajUVOh.iKyLyLyLyLyPyLxXyMzPCL3HBHRUlckImXM8FYk0iHv3BLzDiM1XiM1bSNvfCMy.SLh.RaogGSuM1Z8HBLh.RcocUZjQGZ8HRNyTiHfTWZHUVZmgFc8HBMyTiHu3C.XUkazkFcrUFY.f..Y.fI.rB.3..P.fD.MAvW.PF.oE..ATP.GDPBAvP.ND.EAbQ.dDvHATR.pLPf........BD..........X...................CnH"
                                    },
                                    "fileref": {
                                        "name": "ValhallaVintageVerb[1]",
                                        "filename": "ValhallaVintageVerb[1].maxsnap",
                                        "filepath": "~/Documents/Max 9/Snapshots",
                                        "filepos": -1,
                                        "snapshotfileid": "d52fcc2680d11abf30702d2cf8cda422"
                                    }
                                }
                            ]
                        }
                    },
                    "text": "vst~ C74_AU:/ValhallaVintageVerb",
                    "varname": "vst~",
                    "viewvisibility": 1
                }
            },
            {
                "box": {
                    "id": "obj-78",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 558.0, 81.0, 29.5, 22.0 ],
                    "text": "0"
                }
            },
            {
                "box": {
                    "id": "obj-66",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "signal" ],
                    "patching_rect": [ 1017.0, 519.0, 114.0, 22.0 ],
                    "text": "r~ braille_master_R"
                }
            },
            {
                "box": {
                    "id": "obj-67",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "signal" ],
                    "patching_rect": [ 896.0, 519.0, 112.0, 22.0 ],
                    "text": "r~ braille_master_L"
                }
            },
            {
                "box": {
                    "id": "obj-65",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 591.0, 902.0, 116.0, 22.0 ],
                    "text": "s~ braille_master_R"
                }
            },
            {
                "box": {
                    "id": "obj-64",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 465.0, 902.0, 114.0, 22.0 ],
                    "text": "s~ braille_master_L"
                }
            },
            {
                "box": {
                    "id": "obj-58",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 601.0, 194.0, 116.0, 22.0 ],
                    "text": "s~ braille_master_R"
                }
            },
            {
                "box": {
                    "id": "obj-57",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 478.0, 194.0, 114.0, 22.0 ],
                    "text": "s~ braille_master_L"
                }
            },
            {
                "box": {
                    "id": "obj-5",
                    "maxclass": "button",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 743.0, 224.0, 24.0, 24.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-3",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 524.0, 37.0, 201.0, 22.0 ],
                    "text": "open Mx_FullMix_L18_144bpm.wav"
                }
            },
            {
                "box": {
                    "id": "obj-1",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 3,
                    "outlettype": [ "signal", "signal", "bang" ],
                    "patching_rect": [ 524.0, 129.0, 57.0, 22.0 ],
                    "text": "sfplay~ 2"
                }
            },
            {
                "box": {
                    "id": "obj-102",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1346.0, 281.0, 207.0, 22.0 ],
                    "text": "stem_player 08_WW_bsn2.wav bsn2"
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
                    "patching_rect": [ 321.0, 811.0, 24.0, 24.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-74",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 209.0, 812.0, 109.0, 22.0 ],
                    "text": "s~ braille_playgate"
                }
            },
            {
                "box": {
                    "id": "obj-73",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 90.0, 812.0, 112.0, 22.0 ],
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
                    "patching_rect": [ 165.0, 760.0, 108.0, 22.0 ],
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
                    "patching_rect": [ 152.0, 703.0, 59.0, 22.0 ],
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
                    "patching_rect": [ 152.0, 609.0, 24.0, 24.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-62",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [ "", "" ],
                    "patching_rect": [ 152.0, 670.0, 51.0, 22.0 ],
                    "text": "zl reg"
                }
            },
            {
                "box": {
                    "id": "obj-60",
                    "maxclass": "ezdac~",
                    "numinlets": 2,
                    "numoutlets": 0,
                    "patching_rect": [ 922.0, 734.0, 45.0, 45.0 ]
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
                    "patching_rect": [ 922.0, 575.0, 48.0, 136.0 ],
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
                    "patching_rect": [ 1572.0, 598.0, 209.0, 22.0 ],
                    "text": "stem_player 29_OTH_stem.wav stem"
                }
            },
            {
                "box": {
                    "id": "obj-53",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1574.0, 565.0, 212.0, 22.0 ],
                    "text": "stem_player 28_OTH_room.wav room"
                }
            },
            {
                "box": {
                    "id": "obj-51",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1351.0, 598.0, 203.0, 22.0 ],
                    "text": "stem_player 27_OTH_riser.wav riser"
                }
            },
            {
                "box": {
                    "id": "obj-48",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1345.0, 565.0, 216.0, 22.0 ],
                    "text": "stem_player 26_OTH_crash.wav crash"
                }
            },
            {
                "box": {
                    "id": "obj-46",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1347.0, 493.0, 181.0, 22.0 ],
                    "text": "stem_player 25_STR_cb.wav cb"
                }
            },
            {
                "box": {
                    "id": "obj-45",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1347.0, 463.0, 180.0, 22.0 ],
                    "text": "stem_player 24_STR_vc.wav vc"
                }
            },
            {
                "box": {
                    "id": "obj-44",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1345.0, 435.0, 187.0, 22.0 ],
                    "text": "stem_player 23_STR_vla.wav vla"
                }
            },
            {
                "box": {
                    "id": "obj-43",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1345.0, 402.0, 200.0, 22.0 ],
                    "text": "stem_player 22_STR_vln2.wav vln2"
                }
            },
            {
                "box": {
                    "id": "obj-42",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1345.0, 370.0, 200.0, 22.0 ],
                    "text": "stem_player 21_STR_vln1.wav vln1"
                }
            },
            {
                "box": {
                    "id": "obj-39",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1588.0, 469.0, 183.0, 22.0 ],
                    "text": "stem_player 20_PRC_sn.wav sn"
                }
            },
            {
                "box": {
                    "id": "obj-38",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1588.0, 437.0, 184.0, 22.0 ],
                    "text": "stem_player 19_PRC_bd.wav bd"
                }
            },
            {
                "box": {
                    "id": "obj-37",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1588.0, 404.0, 188.0, 22.0 ],
                    "text": "stem_player 18_PRC_glk.wav glk"
                }
            },
            {
                "box": {
                    "id": "obj-36",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1578.0, 308.0, 177.0, 22.0 ],
                    "text": "stem_player 17_BRS_tb.wav tb"
                }
            },
            {
                "box": {
                    "id": "obj-34",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1578.0, 277.0, 203.0, 22.0 ],
                    "text": "stem_player 16_BRS_tbn2.wav tbn2"
                }
            },
            {
                "box": {
                    "id": "obj-33",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1578.0, 248.0, 203.0, 22.0 ],
                    "text": "stem_player 15_BRS_tbn1.wav tbn1"
                }
            },
            {
                "box": {
                    "id": "obj-32",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1578.0, 220.0, 197.0, 22.0 ],
                    "text": "stem_player 14_BRS_tpt2.wav tpt2"
                }
            },
            {
                "box": {
                    "id": "obj-30",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1578.0, 192.0, 197.0, 22.0 ],
                    "text": "stem_player 13_BRS_tpt1.wav tpt1"
                }
            },
            {
                "box": {
                    "id": "obj-28",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1578.0, 164.0, 190.0, 22.0 ],
                    "text": "stem_player 12_BRS_fh4.wav fh4"
                }
            },
            {
                "box": {
                    "id": "obj-26",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1578.0, 134.0, 189.0, 22.0 ],
                    "text": "stem_player 11_BRS_fh3.wav fh3"
                }
            },
            {
                "box": {
                    "id": "obj-24",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1578.0, 106.0, 190.0, 22.0 ],
                    "text": "stem_player 10_BRS_fh2.wav fh2"
                }
            },
            {
                "box": {
                    "id": "obj-21",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1578.0, 77.0, 190.0, 22.0 ],
                    "text": "stem_player 09_BRS_fh1.wav fh1"
                }
            },
            {
                "box": {
                    "id": "obj-20",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1346.0, 253.0, 207.0, 22.0 ],
                    "text": "stem_player 07_WW_bsn1.wav bsn1"
                }
            },
            {
                "box": {
                    "id": "obj-18",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1346.0, 225.0, 185.0, 22.0 ],
                    "text": "stem_player 06_WW_cl2.wav cl2"
                }
            },
            {
                "box": {
                    "id": "obj-16",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1346.0, 196.0, 185.0, 22.0 ],
                    "text": "stem_player 05_WW_cl1.wav cl1"
                }
            },
            {
                "box": {
                    "id": "obj-14",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1345.0, 167.0, 195.0, 22.0 ],
                    "text": "stem_player 04_WW_ob2.wav ob2"
                }
            },
            {
                "box": {
                    "id": "obj-12",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1344.0, 138.0, 195.0, 22.0 ],
                    "text": "stem_player 03_WW_ob1.wav ob1"
                }
            },
            {
                "box": {
                    "id": "obj-8",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1343.0, 110.0, 180.0, 22.0 ],
                    "text": "stem_player 02_WW_fl2.wav fl2"
                }
            },
            {
                "box": {
                    "id": "obj-7",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "signal" ],
                    "patching_rect": [ 810.0, 447.0, 103.0, 22.0 ],
                    "text": "r~ braille_stem_R"
                }
            },
            {
                "box": {
                    "id": "obj-6",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "signal" ],
                    "patching_rect": [ 502.0, 447.0, 101.0, 22.0 ],
                    "text": "r~ braille_stem_L"
                }
            },
            {
                "box": {
                    "id": "obj-70",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 0,
                    "patching_rect": [ 1343.0, 81.0, 180.0, 22.0 ],
                    "text": "stem_player 01_WW_fl1.wav fl1"
                }
            },
            {
                "box": {
                    "id": "obj-63",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 282.0, 703.0, 49.0, 22.0 ],
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
                    "patching_rect": [ 232.0, 703.0, 41.0, 22.0 ],
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
                    "patching_rect": [ 116.0, 703.0, 31.0, 22.0 ],
                    "text": "stop"
                }
            },
            {
                "box": {
                    "id": "obj-49",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 257.0, 611.0, 163.0, 20.0 ],
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
                    "patching_rect": [ 184.0, 610.0, 68.0, 22.0 ],
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
                    "patching_rect": [ 208.0, 466.0, 55.0, 22.0 ],
                    "text": "pak 0. 0."
                }
            },
            {
                "box": {
                    "id": "obj-35",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 292.0, 564.0, 186.0, 20.0 ],
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
                    "patching_rect": [ 208.0, 563.0, 82.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-29",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 208.0, 518.0, 82.0, 22.0 ],
                    "text": "expr $f1 + $f2"
                }
            },
            {
                "box": {
                    "id": "obj-27",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 425.0, 250.0, 114.0, 20.0 ],
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
                    "patching_rect": [ 371.0, 359.0, 85.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-23",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 371.0, 308.0, 67.0, 22.0 ],
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
                    "patching_rect": [ 371.0, 249.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-19",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 102.0, 249.0, 59.0, 20.0 ],
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
                    "patching_rect": [ 14.0, 131.0, 150.0, 47.0 ],
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
                    "patching_rect": [ 122.0, 316.0, 237.0, 47.0 ],
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
                    "patching_rect": [ 47.0, 373.0, 93.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-11",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 47.0, 335.0, 67.0, 22.0 ],
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
                    "patching_rect": [ 47.0, 292.0, 29.5, 22.0 ],
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
                    "patching_rect": [ 47.0, 248.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-89",
                    "maxclass": "panel",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 1327.0, 33.0, 234.53330570459366, 293.8000250160694 ]
                }
            },
            {
                "box": {
                    "id": "obj-92",
                    "maxclass": "panel",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 1563.0, 33.0, 233.33334028720856, 312.99998968839645 ]
                }
            },
            {
                "box": {
                    "id": "obj-94",
                    "maxclass": "panel",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 1564.0, 348.0, 232.5333028435707, 179.46670797467232 ]
                }
            },
            {
                "box": {
                    "id": "obj-96",
                    "maxclass": "panel",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 1327.0, 330.0, 234.4666497707367, 198.00000590085983 ]
                }
            },
            {
                "box": {
                    "id": "obj-98",
                    "maxclass": "panel",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 1327.0, 530.0, 469.5333028435707, 110.5 ]
                }
            }
        ],
        "lines": [
            {
                "patchline": {
                    "destination": [ "obj-57", 0 ],
                    "source": [ "obj-1", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-58", 0 ],
                    "source": [ "obj-1", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-11", 0 ],
                    "source": [ "obj-10", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-107", 0 ],
                    "source": [ "obj-101", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-78", 0 ],
                    "order": 1,
                    "source": [ "obj-101", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-79", 0 ],
                    "midpoints": [ 316.5, 180.0, 1314.0, 180.0, 1314.0, 709.55078125, 1343.5, 709.55078125 ],
                    "order": 0,
                    "source": [ "obj-101", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-1", 0 ],
                    "midpoints": [ 282.5, 693.0, 482.3046875, 693.0, 482.3046875, 282.0, 549.0, 282.0, 549.0, 228.0, 465.0, 228.0, 465.0, 126.0, 533.5, 126.0 ],
                    "source": [ "obj-104", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-103", 0 ],
                    "source": [ "obj-105", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-103", 0 ],
                    "source": [ "obj-106", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-110", 0 ],
                    "source": [ "obj-107", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-54", 0 ],
                    "midpoints": [ 752.5, 432.0, 125.5, 432.0 ],
                    "source": [ "obj-108", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-86", 0 ],
                    "midpoints": [ 765.5, 489.0, 489.0, 489.0, 489.0, 661.484375, 217.5, 661.484375 ],
                    "source": [ "obj-108", 1 ]
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
                    "destination": [ "obj-111", 0 ],
                    "source": [ "obj-110", 2 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-112", 0 ],
                    "source": [ "obj-110", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-5", 0 ],
                    "source": [ "obj-110", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-22", 0 ],
                    "source": [ "obj-111", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-112", 0 ]
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
                    "destination": [ "obj-40", 0 ],
                    "source": [ "obj-2", 0 ]
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
                    "destination": [ "obj-1", 0 ],
                    "source": [ "obj-3", 0 ]
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
                    "destination": [ "obj-52", 0 ],
                    "source": [ "obj-4", 0 ]
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
                    "order": 1,
                    "source": [ "obj-47", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-86", 1 ],
                    "order": 0,
                    "source": [ "obj-47", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-108", 0 ],
                    "source": [ "obj-5", 0 ]
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
                    "destination": [ "obj-64", 0 ],
                    "source": [ "obj-56", 0 ]
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
                    "destination": [ "obj-81", 0 ],
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
                    "destination": [ "obj-59", 1 ],
                    "source": [ "obj-66", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-59", 0 ],
                    "source": [ "obj-67", 0 ]
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
                    "destination": [ "obj-65", 0 ],
                    "source": [ "obj-69", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-81", 1 ],
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
                    "destination": [ "obj-101", 0 ],
                    "order": 0,
                    "source": [ "obj-75", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-90", 0 ],
                    "order": 1,
                    "source": [ "obj-75", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-56", 1 ],
                    "source": [ "obj-77", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-1", 0 ],
                    "source": [ "obj-78", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-103", 0 ],
                    "source": [ "obj-79", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-69", 1 ],
                    "source": [ "obj-80", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-56", 0 ],
                    "source": [ "obj-81", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-69", 0 ],
                    "source": [ "obj-81", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-85", 0 ],
                    "source": [ "obj-83", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-77", 0 ],
                    "order": 1,
                    "source": [ "obj-84", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-80", 0 ],
                    "order": 0,
                    "source": [ "obj-84", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-106", 0 ],
                    "source": [ "obj-85", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-68", 0 ],
                    "midpoints": [ 1271.0, 908.8515625, 1121.5, 908.8515625, 1121.5, 950.15625, 356.5, 950.15625, 356.5, 655.640625, 176.5, 655.640625, 176.5, 605.5, 161.5, 605.5 ],
                    "source": [ "obj-85", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-79", 0 ],
                    "source": [ "obj-85", 2 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-104", 0 ],
                    "source": [ "obj-86", 0 ]
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
            "obj-102::obj-7": [ "live.gain~[47]", "live.gain~", 0 ],
            "obj-12::obj-7": [ "live.gain~[25]", "live.gain~", 0 ],
            "obj-14::obj-7": [ "live.gain~[24]", "live.gain~", 0 ],
            "obj-16::obj-7": [ "live.gain~[23]", "live.gain~", 0 ],
            "obj-18::obj-7": [ "live.gain~[22]", "live.gain~", 0 ],
            "obj-20::obj-7": [ "live.gain~[21]", "live.gain~", 0 ],
            "obj-21::obj-7": [ "live.gain~[20]", "live.gain~", 0 ],
            "obj-24::obj-7": [ "live.gain~[19]", "live.gain~", 0 ],
            "obj-26::obj-7": [ "live.gain~[18]", "live.gain~", 0 ],
            "obj-28::obj-7": [ "live.gain~[17]", "live.gain~", 0 ],
            "obj-30::obj-7": [ "live.gain~[16]", "live.gain~", 0 ],
            "obj-32::obj-7": [ "live.gain~[15]", "live.gain~", 0 ],
            "obj-33::obj-7": [ "live.gain~[14]", "live.gain~", 0 ],
            "obj-34::obj-7": [ "live.gain~[13]", "live.gain~", 0 ],
            "obj-36::obj-7": [ "live.gain~[12]", "live.gain~", 0 ],
            "obj-37::obj-7": [ "live.gain~[11]", "live.gain~", 0 ],
            "obj-38::obj-7": [ "live.gain~[10]", "live.gain~", 0 ],
            "obj-39::obj-7": [ "live.gain~[9]", "live.gain~", 0 ],
            "obj-42::obj-7": [ "live.gain~[44]", "live.gain~", 0 ],
            "obj-43::obj-7": [ "live.gain~[8]", "live.gain~", 0 ],
            "obj-44::obj-7": [ "live.gain~[7]", "live.gain~", 0 ],
            "obj-45::obj-7": [ "live.gain~[6]", "live.gain~", 0 ],
            "obj-46::obj-7": [ "live.gain~[5]", "live.gain~", 0 ],
            "obj-48::obj-7": [ "live.gain~[4]", "live.gain~", 0 ],
            "obj-51::obj-7": [ "live.gain~[3]", "live.gain~", 0 ],
            "obj-53::obj-7": [ "live.gain~[2]", "live.gain~", 0 ],
            "obj-55::obj-7": [ "live.gain~[1]", "live.gain~", 0 ],
            "obj-59": [ "live.gain~[28]", "live.gain~[28]", 0 ],
            "obj-70::obj-7": [ "live.gain~[46]", "live.gain~", 0 ],
            "obj-77": [ "mix_L", "mix_L", 0 ],
            "obj-80": [ "mix_R", "mix_R", 0 ],
            "obj-81": [ "vst~", "vst~", 0 ],
            "obj-84": [ "Mix[1]", "MIx", 0 ],
            "obj-8::obj-7": [ "live.gain~[26]", "live.gain~", 0 ],
            "parameter_overrides": {
                "obj-102::obj-7": {
                    "parameter_longname": "live.gain~[47]"
                },
                "obj-12::obj-7": {
                    "parameter_longname": "live.gain~[25]"
                },
                "obj-14::obj-7": {
                    "parameter_longname": "live.gain~[24]"
                },
                "obj-16::obj-7": {
                    "parameter_longname": "live.gain~[23]"
                },
                "obj-18::obj-7": {
                    "parameter_longname": "live.gain~[22]"
                },
                "obj-20::obj-7": {
                    "parameter_longname": "live.gain~[21]"
                },
                "obj-21::obj-7": {
                    "parameter_longname": "live.gain~[20]"
                },
                "obj-24::obj-7": {
                    "parameter_longname": "live.gain~[19]"
                },
                "obj-26::obj-7": {
                    "parameter_longname": "live.gain~[18]"
                },
                "obj-28::obj-7": {
                    "parameter_longname": "live.gain~[17]"
                },
                "obj-30::obj-7": {
                    "parameter_longname": "live.gain~[16]"
                },
                "obj-32::obj-7": {
                    "parameter_longname": "live.gain~[15]"
                },
                "obj-33::obj-7": {
                    "parameter_longname": "live.gain~[14]"
                },
                "obj-34::obj-7": {
                    "parameter_longname": "live.gain~[13]"
                },
                "obj-36::obj-7": {
                    "parameter_longname": "live.gain~[12]"
                },
                "obj-37::obj-7": {
                    "parameter_longname": "live.gain~[11]"
                },
                "obj-38::obj-7": {
                    "parameter_longname": "live.gain~[10]"
                },
                "obj-39::obj-7": {
                    "parameter_longname": "live.gain~[9]"
                },
                "obj-42::obj-7": {
                    "parameter_longname": "live.gain~[44]"
                },
                "obj-43::obj-7": {
                    "parameter_longname": "live.gain~[8]"
                },
                "obj-44::obj-7": {
                    "parameter_longname": "live.gain~[7]"
                },
                "obj-45::obj-7": {
                    "parameter_longname": "live.gain~[6]"
                },
                "obj-46::obj-7": {
                    "parameter_longname": "live.gain~[5]"
                },
                "obj-48::obj-7": {
                    "parameter_longname": "live.gain~[4]"
                },
                "obj-51::obj-7": {
                    "parameter_longname": "live.gain~[3]"
                },
                "obj-53::obj-7": {
                    "parameter_longname": "live.gain~[2]"
                },
                "obj-55::obj-7": {
                    "parameter_longname": "live.gain~[1]"
                },
                "obj-70::obj-7": {
                    "parameter_longname": "live.gain~[46]"
                },
                "obj-8::obj-7": {
                    "parameter_longname": "live.gain~[26]"
                }
            },
            "inherited_shortname": 1
        },
        "autosave": 0,
        "snapshot": {
            "filetype": "C74Snapshot",
            "version": 2,
            "minorversion": 0,
            "name": "snapshotlist",
            "origin": "jpatcher",
            "type": "list",
            "subtype": "Undefined",
            "embed": 1,
            "snapshot": {
                "valuedictionary": {
                    "parameter_values": {
                        "Mix[1]": 0.283464566929134,
                        "live.gain~[10]": 0.0,
                        "live.gain~[11]": 0.0,
                        "live.gain~[12]": 0.0,
                        "live.gain~[13]": 0.0,
                        "live.gain~[14]": 0.0,
                        "live.gain~[15]": 0.0,
                        "live.gain~[16]": 0.0,
                        "live.gain~[17]": 0.0,
                        "live.gain~[18]": 0.0,
                        "live.gain~[19]": 0.0,
                        "live.gain~[1]": 0.0,
                        "live.gain~[20]": 0.0,
                        "live.gain~[21]": 0.0,
                        "live.gain~[22]": 0.0,
                        "live.gain~[23]": 0.0,
                        "live.gain~[24]": 0.0,
                        "live.gain~[28]": -0.24644857537137854,
                        "live.gain~[2]": 0.0,
                        "live.gain~[30]": 0.0,
                        "live.gain~[31]": 0.0,
                        "live.gain~[32]": 0.0,
                        "live.gain~[33]": 0.0,
                        "live.gain~[34]": 0.0,
                        "live.gain~[3]": 0.0,
                        "live.gain~[4]": 0.0,
                        "live.gain~[5]": 0.0,
                        "live.gain~[6]": 0.0,
                        "live.gain~[7]": 0.0,
                        "live.gain~[8]": 0.0,
                        "live.gain~[9]": 0.0,
                        "mix_R": 0.283464566929134,
                        "blob": {
                            "mix_L": [ 0.283464566929134 ],
                            "vst~": [
                                {
                                    "filetype": "C74Snapshot",
                                    "version": 2,
                                    "minorversion": 0,
                                    "name": "ValhallaVintageVerb",
                                    "origin": "ValhallaVintageVerb.auinfo",
                                    "type": "AudioUnit",
                                    "subtype": "AudioEffect",
                                    "embed": 1,
                                    "snapshot": {
                                        "pluginname": "ValhallaVintageVerb.auinfo",
                                        "plugindisplayname": "ValhallaVintageVerb",
                                        "pluginsavedname": "",
                                        "pluginsaveduniqueid": 2018798117,
                                        "version": 1,
                                        "isbank": 0,
                                        "isbase64": 1,
                                        "sliderorder": [],
                                        "slidervisibility": [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
                                        "blob": "986.hAGaoMGcv.C1AHv.DTfAGfPBJrvDTTgEWvUag4VclE1XzUmbkIGUjEFcgwUYrUVak4Fcs3VXsU1UyUmXzkGbkckckI2bo8laTQWdvU1WP7fZ0MVYPwVcmklaSQWXzUFUtEVakIwaDklaOAAk..............PD....v7Cf......PL9.H......HiOWmjL....y7Cf.......M+........TyOe7Gd....13y3u1M...vM.........fyO........47Cf.....XvG+.H.....F.hO6gUb..fAg3ivOxE..XfH+bQKNB..FLB.......fAj3ipptJ..XPI8nhpqJMCM3PDQESTxD8CPDELUkjavUGcQ+fDV8TczAWczIgckU1LP.fDgUmY38TDBLkUCISHJI...vyO30FafXWYxMWZu4VOhDiKvHBHk41XuQVZtcVOhTEUF0BNh7iOfviUgwFZgwFagYUZtQWXmUlUkImXf.Ga0cVZtYUYxMWZu4VOhHiKw3hLh.BbxU1bkQmSg0VY8HBQkYVX0wFch.RSogWOhDiKvHBHPIWYDUFagkWOh.iKyPCLxLCMyXSNvLSN0LSM0HBHDU1XgkWOh.iKxTSNvfiLvDSNyHSNvbSLh.xTooWY8HBLtPCMyfCM2XSM1HSMh.RPzQWXisVOh.iK0HBHBE1by0TcrQWOh.iK1HyLvLCN2XCN2XCNyDCL0HBHBE1byg0a1Ulb8HBLtPCMzbCLwDCL0LSM1HSL1PiHffTZmg1TnUFal0iHv3BLh.BRocFZFIWYw0iHv3BNxLSM3LSN1.SMyLSLzHSLh.RQgIGa4QTZlYVcyk1at0iHv3hMzXSL4DCMwfSL2.SNxjiHfvTXzUFQoYlY0MWZu4VOhDiKvHBHM8FYREFck0iHv3hLzTCM0PSM1PiM4.SM3jSNh.RSuQFQkAGcn0iHv3xL2jSN4jSN4TiLyDiMxfCMh.BRocFZCUGc8HBLtfCL1PSNzDSL1bCNyDCMxDiHfvza2MTcz0iHv3RLxTSNxbyMyDyL4PyM1bCNh.xPuw1ax0zajUVOh.iKyLyLyLyLyPyLxXyMzPCL3HBHRUlckImXM8FYk0iHv3BLzDiM1XiM1bSNvfCMy.SLh.RaogGSuM1Z8HBLh.RcocUZjQGZ8HRNyTiHfTWZHUVZmgFc8HBMyTiHu3C.XUkazkFcrUFY.f..Y.fI.rB.3..P.fD.MAvW.PF.oE..ATP.GDPBAvP.ND.EAbQ.dDvHATR.pLPf........BD..........X...................CnH"
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            "snapshotlist": {
                "current_snapshot": 1,
                "entries": [
                    {
                        "filetype": "C74Snapshot",
                        "version": 2,
                        "minorversion": 0,
                        "name": "reverb_v1",
                        "origin": "main",
                        "type": "patcher",
                        "subtype": "Undefined",
                        "embed": 1,
                        "snapshot": {
                            "valuedictionary": {
                                "parameter_values": {
                                    "live.dial": 0.30708661417322825,
                                    "live.gain~[10]": 0.0,
                                    "live.gain~[11]": 0.0,
                                    "live.gain~[12]": 0.0,
                                    "live.gain~[13]": 0.0,
                                    "live.gain~[14]": 0.0,
                                    "live.gain~[15]": 0.0,
                                    "live.gain~[16]": 0.0,
                                    "live.gain~[17]": 0.0,
                                    "live.gain~[18]": 0.0,
                                    "live.gain~[19]": 0.0,
                                    "live.gain~[1]": 0.0,
                                    "live.gain~[20]": 0.0,
                                    "live.gain~[21]": 0.0,
                                    "live.gain~[22]": 0.0,
                                    "live.gain~[23]": 0.0,
                                    "live.gain~[24]": 0.0,
                                    "live.gain~[28]": 0.0,
                                    "live.gain~[2]": 0.0,
                                    "live.gain~[30]": 0.0,
                                    "live.gain~[31]": 0.0,
                                    "live.gain~[32]": 0.0,
                                    "live.gain~[33]": 0.0,
                                    "live.gain~[34]": 0.0,
                                    "live.gain~[3]": 0.0,
                                    "live.gain~[4]": 0.0,
                                    "live.gain~[5]": 0.0,
                                    "live.gain~[6]": 0.0,
                                    "live.gain~[7]": 0.0,
                                    "live.gain~[8]": 0.0,
                                    "live.gain~[9]": 0.0,
                                    "blob": {
                                        "vst~": [
                                            {
                                                "filetype": "C74Snapshot",
                                                "version": 2,
                                                "minorversion": 0,
                                                "name": "ValhallaVintageVerb",
                                                "origin": "ValhallaVintageVerb.auinfo",
                                                "type": "AudioUnit",
                                                "subtype": "AudioEffect",
                                                "embed": 1,
                                                "snapshot": {
                                                    "pluginname": "ValhallaVintageVerb.auinfo",
                                                    "plugindisplayname": "ValhallaVintageVerb",
                                                    "pluginsavedname": "",
                                                    "pluginsaveduniqueid": 2018798117,
                                                    "version": 1,
                                                    "isbank": 0,
                                                    "isbase64": 1,
                                                    "sliderorder": [],
                                                    "slidervisibility": [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
                                                    "blob": "1001.hAGaoMGcv.C1AHv.DTfAGfPBJrvDTTgEWvUag4VclE1XzUmbkIGUjEFcgwUYrUVak4Fcs3VXsU1UyUmXzkGbkckckI2bo8laTQWdvU1WP7fZ0MVYPwVcmklaSQWXzUFUtEVakIwaDklaOAAk..............PD....v7Cf......PL9.H......HiOWmjL....y7Cf.......M+........TyOe7Gd....13y3u1M...vM.........fyO........47Cf.....XvG+.H.....F.hO6gUb..fAg3ivOxE..XfH+bQKNB..FLB.......fAj3ipptJ..XPI8nhpqJMCM3PDQESTxD8CPDELUkjavUGcQ+fDV8TczAWczIgckU1LP.fDgUmY38TDBHlUCISHYI...vyO30FafXWYxMWZu4VOhDiKvHBHk41XuQVZtcVOhTEUF0BNh7iOfviUgwFZgwFagYUZtQWXmUlUkImXf.Ga0cVZtYUYxMWZu4VOhHiKw3hLh.BbxU1bkQmSg0VY8HBQkYVX0wFch.RSogWOh.iKy.yMvfiM1DiM2TCM0LSL4HBHPIWYDUFagkWOh.iKyPCLxLCMyXSNvLSN0LSM0HBHDU1XgkWOh.iKxTSNvfiLvDSNyHSNvbSLh.xTooWY8HBLtPCMyfCM2XSM1HSMh.RPzQWXisVOh.iK0HBHBE1by0TcrQWOh.iK1HyLvLCN2XCN2XCNyDCL0HBHBE1byg0a1Ulb8HBLtPCMzbCLwDCL0LSM1HSL1PiHffTZmg1TnUFal0iHv3BLh.BRocFZFIWYw0iHv3BNxLSM3LSN1.SMyLSLzHSLh.RQgIGa4QTZlYVcyk1at0iHv3hMzXSL4DCMwfSL2.SNxjiHfvTXzUFQoYlY0MWZu4VOhDiKvHBHM8FYREFck0iHv3hLzTCM0PSM1PiM4.SM3jSNh.RSuQFQkAGcn0iHv3xL2jSN4jSN4TiLyDiMxfCMh.BRocFZCUGc8HBLtfCL1PSNzDSL1bCNyDCMxDiHfvza2MTcz0iHv3RLxTSNxbyMyDyL4PyM1bCNh.xPuw1ax0zajUVOh.iKyLyLyLyLyPyLxXyMzPCL3HBHRUlckImXM8FYk0iHv3BLzDiM1XiM1bSNvfCMy.SLh.RaogGSuM1Z8HBLh.RcocUZjQGZ8HRNyTiHfTWZHUVZmgFc8HBMyTiHu3C.XUkazkFcrUFY.f..Y.fI.rB.3..P.fD.MAvW.PF.oE..ATP.GDPBAvP.ND.EAbQ.dDvHATR.pL.j........BD..........X...................CjI"
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        },
                        "fileref": {
                            "name": "main",
                            "filename": "main.maxsnap",
                            "filepath": "~/Documents/Max 9/Snapshots",
                            "filepos": -1,
                            "snapshotfileid": "132e97b5daa0562001b86329a7b81e44"
                        }
                    },
                    {
                        "filetype": "C74Snapshot",
                        "version": 2,
                        "minorversion": 0,
                        "name": "reverb_auxSend",
                        "origin": "main",
                        "type": "patcher",
                        "subtype": "Undefined",
                        "embed": 1,
                        "snapshot": {
                            "valuedictionary": {
                                "parameter_values": {
                                    "Mix[1]": 0.283464566929134,
                                    "live.gain~[10]": 0.0,
                                    "live.gain~[11]": 0.0,
                                    "live.gain~[12]": 0.0,
                                    "live.gain~[13]": 0.0,
                                    "live.gain~[14]": 0.0,
                                    "live.gain~[15]": 0.0,
                                    "live.gain~[16]": 0.0,
                                    "live.gain~[17]": 0.0,
                                    "live.gain~[18]": 0.0,
                                    "live.gain~[19]": 0.0,
                                    "live.gain~[1]": 0.0,
                                    "live.gain~[20]": 0.0,
                                    "live.gain~[21]": 0.0,
                                    "live.gain~[22]": 0.0,
                                    "live.gain~[23]": 0.0,
                                    "live.gain~[24]": 0.0,
                                    "live.gain~[28]": -0.24644857537137854,
                                    "live.gain~[2]": 0.0,
                                    "live.gain~[30]": 0.0,
                                    "live.gain~[31]": 0.0,
                                    "live.gain~[32]": 0.0,
                                    "live.gain~[33]": 0.0,
                                    "live.gain~[34]": 0.0,
                                    "live.gain~[3]": 0.0,
                                    "live.gain~[4]": 0.0,
                                    "live.gain~[5]": 0.0,
                                    "live.gain~[6]": 0.0,
                                    "live.gain~[7]": 0.0,
                                    "live.gain~[8]": 0.0,
                                    "live.gain~[9]": 0.0,
                                    "mix_R": 0.283464566929134,
                                    "blob": {
                                        "mix_L": [ 0.283464566929134 ],
                                        "vst~": [
                                            {
                                                "filetype": "C74Snapshot",
                                                "version": 2,
                                                "minorversion": 0,
                                                "name": "ValhallaVintageVerb",
                                                "origin": "ValhallaVintageVerb.auinfo",
                                                "type": "AudioUnit",
                                                "subtype": "AudioEffect",
                                                "embed": 1,
                                                "snapshot": {
                                                    "pluginname": "ValhallaVintageVerb.auinfo",
                                                    "plugindisplayname": "ValhallaVintageVerb",
                                                    "pluginsavedname": "",
                                                    "pluginsaveduniqueid": 2018798117,
                                                    "version": 1,
                                                    "isbank": 0,
                                                    "isbase64": 1,
                                                    "sliderorder": [],
                                                    "slidervisibility": [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
                                                    "blob": "986.hAGaoMGcv.C1AHv.DTfAGfPBJrvDTTgEWvUag4VclE1XzUmbkIGUjEFcgwUYrUVak4Fcs3VXsU1UyUmXzkGbkckckI2bo8laTQWdvU1WP7fZ0MVYPwVcmklaSQWXzUFUtEVakIwaDklaOAAk..............PD....v7Cf......PL9.H......HiOWmjL....y7Cf.......M+........TyOe7Gd....13y3u1M...vM.........fyO........47Cf.....XvG+.H.....F.hO6gUb..fAg3ivOxE..XfH+bQKNB..FLB.......fAj3ipptJ..XPI8nhpqJMCM3PDQESTxD8CPDELUkjavUGcQ+fDV8TczAWczIgckU1LP.fDgUmY38TDBLkUCISHJI...vyO30FafXWYxMWZu4VOhDiKvHBHk41XuQVZtcVOhTEUF0BNh7iOfviUgwFZgwFagYUZtQWXmUlUkImXf.Ga0cVZtYUYxMWZu4VOhHiKw3hLh.BbxU1bkQmSg0VY8HBQkYVX0wFch.RSogWOhDiKvHBHPIWYDUFagkWOh.iKyPCLxLCMyXSNvLSN0LSM0HBHDU1XgkWOh.iKxTSNvfiLvDSNyHSNvbSLh.xTooWY8HBLtPCMyfCM2XSM1HSMh.RPzQWXisVOh.iK0HBHBE1by0TcrQWOh.iK1HyLvLCN2XCN2XCNyDCL0HBHBE1byg0a1Ulb8HBLtPCMzbCLwDCL0LSM1HSL1PiHffTZmg1TnUFal0iHv3BLh.BRocFZFIWYw0iHv3BNxLSM3LSN1.SMyLSLzHSLh.RQgIGa4QTZlYVcyk1at0iHv3hMzXSL4DCMwfSL2.SNxjiHfvTXzUFQoYlY0MWZu4VOhDiKvHBHM8FYREFck0iHv3hLzTCM0PSM1PiM4.SM3jSNh.RSuQFQkAGcn0iHv3xL2jSN4jSN4TiLyDiMxfCMh.BRocFZCUGc8HBLtfCL1PSNzDSL1bCNyDCMxDiHfvza2MTcz0iHv3RLxTSNxbyMyDyL4PyM1bCNh.xPuw1ax0zajUVOh.iKyLyLyLyLyPyLxXyMzPCL3HBHRUlckImXM8FYk0iHv3BLzDiM1XiM1bSNvfCMy.SLh.RaogGSuM1Z8HBLh.RcocUZjQGZ8HRNyTiHfTWZHUVZmgFc8HBMyTiHu3C.XUkazkFcrUFY.f..Y.fI.rB.3..P.fD.MAvW.PF.oE..ATP.GDPBAvP.ND.EAbQ.dDvHATR.pLPf........BD..........X...................CnH"
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        },
                        "fileref": {
                            "name": "reverb_v1[1]",
                            "filename": "reverb_v1[1].maxsnap",
                            "filepath": "~/Documents/Max 9/Snapshots",
                            "filepos": -1,
                            "snapshotfileid": "a4a5b8327982fe3c075c87c8a46bcb9e"
                        }
                    }
                ]
            }
        },
        "toolbaradditions": [ "Data Knot" ]
    }
}