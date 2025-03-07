from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from direct.actor import Actor
from direct.particles import ParticleEffect
from direct.particles import Particles
from direct.particles import ForceGroup
from .PooledEffect import PooledEffect
from .EffectController import EffectController
from otp.otpbase import OTPRender
import random
import math

class SeaBottomBubbleEffect(PooledEffect, EffectController):
    cardScale = 128.0

    def __init__(self):
        PooledEffect.__init__(self)
        EffectController.__init__(self)
        model = loader.loadModel('models/effects/particleMaps')
        self.card = model.find('**/pir_t_efx_env_bubble')
        if not SeaBottomBubbleEffect.particleDummy:
            SeaBottomBubbleEffect.particleDummy = render.attachNewNode(ModelNode('SeaBottomBubbleEffectParticleDummy'))
            SeaBottomBubbleEffect.particleDummy.node().setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne))
            SeaBottomBubbleEffect.particleDummy.setDepthWrite(0)
            SeaBottomBubbleEffect.particleDummy.setFogOff()
            SeaBottomBubbleEffect.particleDummy.setLightOff()
            SeaBottomBubbleEffect.particleDummy.setColorScaleOff()
            SeaBottomBubbleEffect.particleDummy.setTwoSided(1)
        self.f = ParticleEffect.ParticleEffect('SeaBottomBubbleEffect')
        self.f.reparentTo(self)
        self.p0 = Particles.Particles('particles-1')
        self.p0.setFactory('PointParticleFactory')
        self.p0.setRenderer('SpriteParticleRenderer')
        self.f.addParticles(self.p0)
        self.f0 = None
        self.setParticleOptions()
        return

    def hide(self):
        NodePath.hide(self)
        SeaBottomBubbleEffect.particleDummy.hide()

    def show(self):
        NodePath.show(self)
        SeaBottomBubbleEffect.particleDummy.show()

    def setLifespanBasedOnDepth(self, fishPos):
        z = math.fabs(fishPos.getZ())
        time = math.sqrt(z) * 1.0
        self.p0.factory.setLifespanBase(time)

    def setParticleOptions(self):
        self.p0.setEmitter('LineEmitter')
        if self.f0 != None:
            self.f.removeForceGroup(self.f0)
        self.f0 = ForceGroup.ForceGroup('gravity')
        force0 = LinearVectorForce(Vec3(0.0, 0.0, 0.05), 1.0, 0)
        force0.setVectorMasks(1, 1, 1)
        force0.setActive(1)
        self.f0.addForce(force0)
        force1 = LinearJitterForce(0.5, 0)
        force1.setVectorMasks(1, 1, 1)
        force1.setActive(1)
        self.f0.addForce(force1)
        self.f.addForceGroup(self.f0)
        self.p0.setPoolSize(10)
        self.p0.setLitterSize(1)
        self.p0.setLitterSpread(0)
        self.p0.setSystemLifespan(0.0)
        self.p0.setLocalVelocityFlag(0)
        self.p0.setSystemGrowsOlderFlag(0)
        self.p0.factory.setMassBase(1.0)
        self.p0.factory.setMassSpread(0.0)
        self.p0.factory.setTerminalVelocityBase(400.0)
        self.p0.factory.setTerminalVelocitySpread(0.0)
        self.p0.renderer.setAlphaMode(BaseParticleRenderer.PRALPHAINOUT)
        self.p0.renderer.setUserAlpha(0.5)
        self.p0.renderer.setFromNode(self.card)
        self.p0.renderer.setXScaleFlag(1)
        self.p0.renderer.setYScaleFlag(1)
        self.p0.renderer.setAnimAngleFlag(1)
        bubbleSize = random.uniform(0.0025, 0.005)
        self.p0.renderer.setInitialXScale(0.002 * self.cardScale)
        self.p0.renderer.setInitialYScale(0.002 * self.cardScale)
        self.p0.renderer.setFinalXScale(0.002 * self.cardScale)
        self.p0.renderer.setFinalYScale(0.002 * self.cardScale)
        self.p0.renderer.setNonanimatedTheta(0.0)
        self.p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PPNOBLEND)
        self.p0.renderer.setAlphaDisable(0)
        self.p0.emitter.setEmissionType(BaseParticleEmitter.ETRADIATE)
        self.p0.emitter.setAmplitude(0.0)
        self.p0.emitter.setAmplitudeSpread(0.0)
        self.p0.emitter.setOffsetForce(Vec3(0.0, 0.0, 1.0))
        self.p0.emitter.setRadiateOrigin(Point3(0.0, 0.0, 0.0))
        return

    def createTrack(self):
        self.setParticleOptions()
        self.startEffect = Sequence(Wait(random.uniform(0.0, 14.0)), Func(self.p0.setBirthRate, 14.0), Func(self.p0.clearToInitial), Func(self.f.start, self, self.particleDummy))
        self.endEffect = Sequence(Func(self.p0.setBirthRate, 100.0), Wait(0.0), Func(self.cleanUpEffect))
        self.track = Sequence(self.startEffect, Wait(1.5), self.endEffect)

    def cleanUpEffect(self):
        EffectController.cleanUpEffect(self)
        self.checkInEffect(self)

    def destroy(self):
        EffectController.destroy(self)
        PooledEffect.destroy(self)