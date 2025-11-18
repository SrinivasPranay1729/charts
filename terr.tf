############################################
# Clean L2 Secondary Region Conditions
############################################

# Secondary Storage RG
count = (var.secondary_storage_rg_name != "" && local.secondary_region_enabled) ? 1 : 0

# Secondary VNet RG
count = (var.secondary_vnet_rg_name != "" && local.secondary_region_enabled) ? 1 : 0

# Secondary KeyVault RG
count = (var.secondary_keyvault_rg_name != "" && local.secondary_region_enabled) ? 1 : 0

# Secondary Network Watcher RG
count = (var.secondary_network_watcher_rg_name != "" && local.secondary_region_enabled) ? 1 : 0

# Secondary Backup RG
count = (var.secondary_backup_rg_name != "" && local.secondary_region_enabled) ? 1 : 0

# Secondary KeyVault Resource
count = (var.secondary_keyvault_name != "" && local.secondary_region_enabled) ? 1 : 0

# Secondary Network Watcher Resource
count = (var.secondary_network_watcher_name != "" && local.secondary_region_enabled) ? 1 : 0

# Secondary VNet (for_each)
for_each = (
  var.secondary_keyvault_name != "" && local.secondary_region_enabled
) ? {
  for key in local.cmk_resource_type_list_secondary:
    key => key
} : {}

# Secondary Virtual Network Name
count = (var.secondary_virtual_network_name != "" && local.secondary_region_enabled) ? 1 : 0

# Secondary Route Table (Primary)
count = (var.secondary_route_table_name != "" && local.secondary_region_enabled) ? 1 : 0

# Secondary Route Table (Additional)
count = (var.secondary_route_table_name != "" && local.secondary_region_enabled) ? 1 : 0




locals {

  # Default behavior:
  # prod -> create secondary
  # uat  -> create secondary
  # others -> do not create secondary
  default_secondary_allowed = (
    local.environment_type == "prod" ? true :
    local.environment_type == "uat"  ? true :
    false
  )

  # Apply override only if provided
  env_secondary_allowed = (
    var.override_secondary_region == null ?
    local.default_secondary_allowed :
    var.override_secondary_region
  )

  # Existing create flags must force enable
  force_secondary = (
    var.create_secondary_vnet ||
    var.create_secondary_rgs  ||
    var.create_secondary_kv   ||
    var.create_secondary_nw   ||
    var.create_secondary_backup ||
    var.create_secondary_route
  )

  # Final one-line flag used everywhere
  secondary_region_enabled = (
    local.force_secondary || local.env_secondary_allowed
  )
}


variable "override_secondary_region" {
  description = "Force enable/disable all secondary region resources. If null, environment defaults apply."
  type        = bool
  default     = null
}



locals {

  # 1. Default based on environment
  env_default_secondary_allowed = (
    local.environment_type == "prod" ? true :
    local.environment_type == "uat"  ? true :
    false
  )

  # 2. Default based on region
  secondary_other_regions = (
    local.primary_region_code == "cus" ? true : false
  )

  # 3. Combined default
  default_secondary_allowed = (
    local.env_default_secondary_allowed && local.secondary_other_regions
  )

  # 4. Override must be applied BEFORE final
  env_secondary_allowed = (
    var.override_secondary_region == null ?
    local.default_secondary_allowed :
    var.override_secondary_region
  )

  # 5. Force flags
  secondary_rg_inputs = (
    var.create_secondary_vnet ||
    var.create_secondary_rgs  ||
    var.create_secondary_kv
  )

  # 6. FINAL (must come last)
  secondary_region_enabled = (
    local.secondary_rg_inputs || local.env_secondary_allowed
  )
}





locals {

  region_default_secondary_allowed = (
    lower(local.primary_region_code) == "cus"
  )

  env_default_secondary_allowed = (
    local.environment_type == "prod" ||
    local.environment_type == "uat"
  )

  default_secondary_allowed = (
    local.region_default_secondary_allowed &&
    local.env_default_secondary_allowed
  )

  # ⭐ INVERTED OVERRIDE (true = disable, false = enable)
  override_secondary = (
    var.override_secondary_region == null ?
    local.default_secondary_allowed :
    !var.override_secondary_region
  )

  force_secondary = (
    local.region_default_secondary_allowed &&
    (var.create_secondary_vnet || var.create_secondary_rgs || var.create_secondary_kv)
  )

  secondary_region_enabled = (
    local.force_secondary || local.override_secondary
  )
}

