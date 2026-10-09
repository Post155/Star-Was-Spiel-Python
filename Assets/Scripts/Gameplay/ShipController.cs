using UnityEngine;

namespace StarWarsUnity
{
    public static class ShipController
    {
        public static void ApplyDefaultMuzzles(ShipDefinition definition)
        {
            if (definition == null) return;
            switch (definition.id)
            {
                case ShipId.XWing:
                    definition.laserMuzzles = new[] { new Vector2(18f, 0.30f * 96f), new Vector2(0.82f * 96f, 0.30f * 96f) };
                    definition.torpedoMuzzle = new Vector2(48f, 0f);
                    definition.moveSpeed = GameConstants.ShipSpeedXWing;
                    definition.canFireTorpedo = true;
                    break;
                case ShipId.MillenniumFalcon:
                    definition.laserMuzzles = new[] { new Vector2(.43f * 96f, .06f * 96f), new Vector2(.58f * 96f, .06f * 96f) };
                    definition.canFireTorpedo = false;
                    definition.moveSpeed = GameConstants.ShipSpeedMillennium;
                    break;
                case ShipId.TieFighter:
                    definition.laserMuzzles = new[] { new Vector2(.44f * 96f, .30f * 96f), new Vector2(.55f * 96f, .30f * 96f) };
                    definition.torpedoMuzzle = new Vector2(.47f * 96f, .12f * 96f);
                    definition.canFireTorpedo = true;
                    definition.moveSpeed = GameConstants.ShipSpeedTieFighter;
                    break;
                case ShipId.BattleDroid:
                    definition.laserMuzzles = new[] { new Vector2(.05f * 96f, .01f * 96f), new Vector2(.94f * 96f, .01f * 96f) };
                    definition.canFireTorpedo = false;
                    definition.moveSpeed = GameConstants.ShipSpeedBattleDroid;
                    break;
            }
        }

        public static Faction FactionFor(ShipDefinition definition)
        {
            return definition != null && (definition.id == ShipId.XWing || definition.id == ShipId.MillenniumFalcon)
                ? Faction.Rebels
                : Faction.Empire;
        }
    }
}
