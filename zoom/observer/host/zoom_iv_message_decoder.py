from zoom.model.zoom_pedalboard import ZoomPedalboard
from zoom.observer.host.protocol import MidiProtocol
from zoom.observer.host.zoomg3v2_patch import ZoomG3v2Patch
from zoom.zoom_builder import ZoomBuilder


class ZoomIVMessageDecoder:
    def decode(self, message):
        # Commands (F0 52 00 5A xx)
        # 08: Specific path
        # 28: Current path / Foot switch expression
        # 31: Global info: Tempo / Signal path / Auto save / Foot switch (min, max)
        # 31: Patch info: Patch name / Patch volume / Ctrl switch assignment
        # 31: Effect param value:
        # 32: Patch saved
        print(message.hex())

        if message.type == 'program_change':
            print('Current patch is', "'" + str(+message.program) + "'")

        elif len(message) == 110:
            print('Current patch', message)

        elif len(message) == 120:
            return self.decode_specific_path(message)

        elif len(message) == 15:
            print('Device info', message.hex())
            print(MidiProtocol.device_identity_reply_decode(message.data))

        else:
            # Path saved in x position
            # F0 52 00 5A 32 01 00 00 xx 00 00 00 00 00 F7
            # Swap xx <--> yy
            # F0 52 00 5A 32 02 00 00 xx 00 00 yy 00 00 F7
            print(message, '\n', message.hex())
            print('Size', len(message))

    def decode_specific_path(self, message):
        builder = ZoomBuilder(None)

        manufacturing_id = message.data[0]
        device_id = message.data[1]
        model_number = message.data[2]

        command_number = message.data[3]  # 08

        name = bytes(message.data[0x65:0x69] + message.data[0x6A:0x70]).decode()

        pedalboard = ZoomPedalboard(name=name)

        for id_effect in range(6):
            # FIXME: Correct efect
            effect = ZoomG3v2Patch.get_effect(builder, message.data[6:], id_effect)
            effect.active = ZoomG3v2Patch.get_effect_status(message.data[6:], id_effect)

            for id_param, param in enumerate(effect.params):
                param.value = ZoomG3v2Patch.get_param(message.data, id_effect, id_param)

            pedalboard.effects.append(effect)
            print(effect.__dict__)

        # TODO: Pedalboard volume
        # TODO: CTRL SW/PDL
        # TODO: PDL DST
