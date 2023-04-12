from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.directnotify import DirectNotifyGlobal
from direct.fsm.FSM import FSM
from otp.distributed.OtpDoGlobals import *
from pirates.uberdog import InventoryInit
from pirates.uberdog.UberDogGlobals import InventoryId, InventoryType

class InventoryFSM(FSM):

    def __init__(self, manager, avatarId, callback):
        self.manager = manager
        self.avatarId = avatarId
        self.callback = callback

        FSM.__init__(self, 'InventoryFSM')

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterStart(self):

        def queryAvatar(dclass, fields):
            if not dclass or not fields:
                return self.notify.warning('Failed to query avatar %d!' % self.avatarId)

            inventoryId, = fields.get('setInventoryId', (0,))

            if not inventoryId:
                self.request('Create')
            else:
                self.request('Load', inventoryId)

        self.manager.air.dbInterface.queryObject(self.manager.air.dbId, self.avatarId, queryAvatar,
            dclass=self.manager.air.dclassesByName['DistributedPlayerPirateUD'])

    def exitStart(self):
        pass

    def enterCreate(self):

        def inventorySet(fields, inventoryId):
            if fields:
                return self.notify.warning('Failed to set inventory %d for %d!' % (inventoryId, self.avatarId))

            self.request('Load', inventoryId)

        def inventoryCreated(inventoryId):
            if not inventoryId:
                return self.notify.warning('Failed to create inventory for %d!' % self.avatarId)

            self.manager.air.dbInterface.updateObject(self.manager.air.dbId, self.avatarId, self.manager.air.dclassesByName['DistributedPlayerPirateUD'],
                {'setInventoryId': (inventoryId,)}, callback=lambda fields: inventorySet(fields, inventoryId))

        accumulators = []
        accumulators.append([InventoryType.OverallRep, 0])

        categoryLimits = []
        for key, limit in InventoryInit.CategoryLimits.items():
            categoryLimits.append((key, limit))

        stackLimits = []
        for key, limit in InventoryInit.StackLimits.items():
            stackLimits.append((key, limit))

        startStacks = []
        for key, amount in InventoryInit.StackStartsWith.items():
            startStacks.append((key, amount))

        self.manager.air.dbInterface.createObject(self.manager.air.dbId, self.manager.air.dclassesByName['PirateInventoryUD'],
            fields={
                'setOwnerId': (self.avatarId,),
                'setInventoryVersion': (InventoryInit.UberDogRevision,),
                'setCategoryLimits': (categoryLimits,),
                'setAccumulators': (accumulators,),
                'setStackLimits': (stackLimits,),
                'setStacks': (startStacks,)
            }, callback=inventoryCreated)

    def exitCreate(self):
        pass

    def enterLoad(self, inventoryId):
        if not inventoryId:
            return self.warning('Failed to activate invalid inventory object!')

        self.manager.air.sendActivate(inventoryId, self.avatarId, OTP_ZONE_ID_MANAGEMENT, dclass=self.manager.air.dclassesByName[
            'PirateInventoryUD'])

        del self.manager.avatar2fsm[self.avatarId]
        self.demand('Off')
        self.callback(inventoryId)

    def exitLoad(self):
        pass

class DistributedInventoryManagerUD(DistributedObjectGlobalUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedInventoryManagerUD')

    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)

        self.avatar2fsm = {}

    def initiateInventory(self, avatarId, callback):
        if not avatarId:
            return self.notify.warning('Failed to initiate inventory for invalid avatar!')

        if not callable(callback):
            self.notify.error('Failed to initiate inventory, callback not callable!')

        if avatarId in self.avatar2fsm:
            return self.notify.warning('Failed to initiate inventory for already existing avatar %s!' % avatarId)

        self.avatar2fsm[avatarId] = InventoryFSM(self, avatarId, callback)
        self.avatar2fsm[avatarId].request('Start')
