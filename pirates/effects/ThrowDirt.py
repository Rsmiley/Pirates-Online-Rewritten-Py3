from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from direct.particles import Particles
from direct.particles import ForceGroup
from .EffectController import EffectController
from .PooledEffect import PooledEffect
import random

class ThrowDirt(PooledEffect, EffectController):
    cardScale = 128.0

    def __init__(self):
        PooledEffect.__init__(self)
        EffectController.__init__(self)
        model = loader.loadModel('models/effects/particleMaps')
        self.card = model.find('**/particleRockShower')
        self.speed = 20.0
        if not ThrowDirt.particleDummy:
            ThrowDirt.particleDummy = render.attachNewNode(ModelNode('ThrowDirtParticleDummy'))
            ThrowDirt.particleDummy.setDepthWrite(0)
            ThrowDirt.particleDummy.setLightOff()
            ThrowDirt.particleDummy.setColorScaleOff()
            ThrowDirt.particleDummy.setFogOff()
        self.f = ParticleEffect.ParticleEffect('ThrowDirt')
        self.f.reparentTo(self)
        self.p0 = Particles.Particles('particles-1')
        self.p0.setFactory('PointParticleFactory')
        self.p0.setRenderer('SpriteParticleRenderer')
        self.p0.setEmitter('DiscEmitter')
        self.f.addParticles(self.p0)
        self.f0 = ForceGroup.ForceGroup('Grav')
        force0 = LinearVectorForce(Vec3(0.0, -1.0, -20.0), 1.0, 1)
        force0.setVectorMasks(1, 1, 1)
        force0.setActive(1)
        self.f0.addForce(force0)
        self.f.addForceGroup(self.f0)
        self.p0.setPoolSize(32)
        self.p0.setBirthRate(0.02)
        self.p0.setLitterSize(1)
        self.p0.setLitterSpread(0)
        self.p0.setSystemLifespan(0.0)
        self.p0.setLocalVelocityFlag(1)
        self.p0.setSystemGrowsOlderFlag(0)
        self.p0.factory.setLifespanBase(2.0)
        self.p0.factory.setLifespanSpread(1.0)
        self.p0.factory.setMassBase(0.4)
        self.p0.factory.setMassSpread(0.35)
        self.p0.factory.setTerminalVelocityBase(400.0)
        self.p0.factory.setTerminalVelocitySpread(0.0)
        self.p0.renderer.setAlphaMode(BaseParticleRenderer.PRALPHAOUT)
        self.p0.renderer.setUserAlpha(1.0)
        self.p0.renderer.setFromNode(self.card)
        self.p0.renderer.setColor(Vec4(0.3, 0.2, 0, 1))
        self.p0.renderer.setXScaleFlag(1)
        self.p0.renderer.setYScaleFlag(1)
        self.p0.renderer.setAnimAngleFlag(0)
        self.p0.renderer.setInitialXScale(0.004 * self.cardScale)
        self.p0.renderer.setFinalXScale(0.008 * self.cardScale)
        self.p0.renderer.setInitialYScale(0.004 * self.cardScale)
        self.p0.renderer.setFinalYScale(0.008 * self.cardScale)
        self.p0.renderer.setNonanimatedTheta(0.0)
        self.p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PPBLENDLINEAR)
        self.p0.renderer.setAlphaDisable(0)
        self.p0.emitter.setEmissionType(BaseParticleEmitter.ETRADIATE)
        self.p0.emitter.setAmplitude(1.5)
        self.p0.emitter.setAmplitudeSpread(0.0)
        self.p0.emitter.setOffsetForce(Vec3(0.0, 10.0, 20.0))
        self.p0.emitter.setExplicitLaunchVector(Vec3(0.0, 0.0, 0.0))
        self.p0.emitter.setRadiateOrigin(Point3(0.0, 0.0, 0.0))
        self.p0.emitter.setRadius(1.0)

    def createTrack(self):
        self.track = Sequence(Func(self.p0.setBirthRate, 0.02), Func(self.p0.clearToInitial), Func(self.f.start, self, self.particleDummy), Wait(0.3), Func(self.p0.setBirthRate, 100), Wait(7.0), Func(self.cleanUpEffect))

    def cleanUpEffect(self):
        EffectController.cleanUpEffect(self)
        self.checkInEffect(self)

    def destroy(self):
        EffectController.destroy(self)
        PooledEffect.destroy(self)