'''Contains core nodes for wxviews'''

from abc import ABC, abstractproperty

class WxNode(ABC):
    '''Node interface'''
    @abstractproperty
    def sizer_args(self) -> dict:
        '''Contains sizer args'''

    @sizer_args.setter
    def sizer_args(self, value):
        '''Contains sizer args'''
