import items,data,entities,events,gui,modifiers,objects,particles
# a set for every runnable object type
def getRunnableTypes():
    return {
        entities.entity:"entities",
        entities.Player:"players",
        items.item:"drops",
        particles.particle:"particles",
        objects.object:"objects",
        events.event:"events",
        projectiles.projectile:"projectiles",
        default.GuiObject:"guis",
    }