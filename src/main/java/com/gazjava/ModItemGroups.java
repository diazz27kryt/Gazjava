package com.gazjava;

import net.fabricmc.fabric.api.itemgroup.v1.FabricItemGroup;
import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

/** Creative inventory placement: a dedicated "GazJava" tab plus the vanilla "Food & Drinks" tab. */
public final class ModItemGroups {
	public static final ResourceKey<CreativeModeTab> GAZJAVA_TAB_KEY =
			ResourceKey.create(Registries.CREATIVE_MODE_TAB, GazJava.id("gazjava"));

	private ModItemGroups() {
	}

	public static void init() {
		CreativeModeTab tab = FabricItemGroup.builder()
				.title(Component.translatable("itemGroup.gazjava"))
				.icon(() -> new ItemStack(ModItems.GAZYAVA_MOTOBRATA))
				.displayItems((parameters, output) -> {
					for (Item drink : ModItems.DRINKS) {
						output.accept(drink);
					}
				})
				.build();
		Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, GAZJAVA_TAB_KEY, tab);

		ItemGroupEvents.modifyEntriesEvent(CreativeModeTabs.FOOD_AND_DRINKS).register(entries -> {
			for (Item drink : ModItems.DRINKS) {
				entries.accept(drink);
			}
		});
	}
}
