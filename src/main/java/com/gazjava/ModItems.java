package com.gazjava;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.Consumable;
import net.minecraft.world.item.component.Consumables;
import net.minecraft.world.item.consume_effects.ApplyStatusEffectsConsumeEffect;

/**
 * Registry of all GazJava items.
 *
 * <p>Every drink is a normal consumable (vanilla drinking animation and sound). After drinking, the
 * stack is converted into an empty glass bottle by the vanilla "use remainder" component; in
 * creative mode vanilla does not consume the item and does not hand out the bottle.
 */
public final class ModItems {
	/** Positive effects every drink grants; only the duration differs between the drinks. */
	private static final List<String> POSITIVE_EFFECTS = List.of(
			"speed",
			"haste",
			"strength",
			"health_boost",
			"regeneration",
			"resistance",
			"fire_resistance",
			"water_breathing",
			"invisibility",
			"night_vision",
			"jump_boost",
			"absorption",
			"slow_falling");

	/** All registered drinks, in the order they appear in the creative tab. */
	public static final List<Item> DRINKS = new ArrayList<>();

	/** Gazyava Nefora - effects last 1 minute. */
	public static final Item GAZYAVA_NEFORA = registerDrink("gazyava_nefora", 60, 2);
	/** Gazyava Ofnika - effects last 5 minutes. */
	public static final Item GAZYAVA_OFNIKA = registerDrink("gazyava_ofnika", 5 * 60, 3);
	/** Gazyava Motobrata - effects last 20 minutes. */
	public static final Item GAZYAVA_MOTOBRATA = registerDrink("gazyava_motobrata", 20 * 60, 4);

	private ModItems() {
	}

	/** Forces class loading so the static registrations above run during mod initialisation. */
	public static void init() {
	}

	private static Item registerDrink(String name, int effectSeconds, int nutrition) {
		ResourceKey<Item> key = ResourceKey.create(Registries.ITEM, GazJava.id(name));

		List<MobEffectInstance> effects = new ArrayList<>();
		for (String effectName : POSITIVE_EFFECTS) {
			effects.add(new MobEffectInstance(effect(effectName), effectSeconds * 20, 0, false, true));
		}
		// A little instant healing on top of the timed effects ("restores some health").
		effects.add(new MobEffectInstance(effect("instant_health"), 1, 0));

		Consumable consumable = Consumables.defaultDrink()
				.onConsume(new ApplyStatusEffectsConsumeEffect(List.copyOf(effects), 1.0f))
				.build();

		// "alwaysEdible" lets the drink be used with a full hunger bar, like a potion.
		FoodProperties food = new FoodProperties.Builder()
				.nutrition(nutrition)
				.saturationModifier(0.3f)
				.alwaysEdible()
				.build();

		Item.Properties properties = new Item.Properties()
				.setId(key)
				.stacksTo(16)
				.food(food, consumable)
				.usingConvertsTo(Items.GLASS_BOTTLE);

		Item item = Registry.register(BuiltInRegistries.ITEM, key, new Item(properties));
		DRINKS.add(item);
		return item;
	}

	private static Holder<MobEffect> effect(String name) {
		Identifier id = Identifier.withDefaultNamespace(name);
		return BuiltInRegistries.MOB_EFFECT.get(id)
				.orElseThrow(() -> new IllegalStateException("Unknown mob effect: " + id));
	}
}
