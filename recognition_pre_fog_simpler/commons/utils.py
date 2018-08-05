# ---------------------------------------------------------
# Name:        utils
# Description: A general tools which is not created with a object
# Author:      Lucas Yu
# Created:     2018-07-16
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------

class PreProcedure:
    @staticmethod
    def create_part_full_field_map(part_field):
        time_field=["time16", "time10", "hour", "minute", "second", "ms"]
        return {part: time_field+[part + "_" + field for field in part_field[part] if field not in time_field] for part in part_field}