package com.gazjava;

import net.fabricmc.api.ModInitializer;
import net.minecraft.resources.Identifier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * GazJava - three fizzy drinks inspired by "Zhivchik".
 */
public class GazJava implements ModInitializer {
	public static final String MOD_ID = "gazjava";
	public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

	public static Identifier id(String path) {
		return Identifier.fromNamespaceAndPath(MOD_ID, path);
	}

	@Override
	public void onInitialize() {
		ModItems.init();
		ModItemGroups.init();
		LOGGER.info("GazJava loaded: {} drinks registered", ModItems.DRINKS.size());
	}
}
