config, shallow, deep = var("config"), var("shallow"), var("deep")
check("shallow is a new dict", lambda: isinstance(shallow, dict) and shallow is not config,
      "config.copy() or copy.copy(config).")
check("shallow shares the inner 'layers' list with config",
      lambda: shallow["layers"] is config["layers"], "A shallow copy only copies the outer dict.")
check("shallow kept its own lr (0.01)", lambda: shallow["lr"] == 0.01)
check("deep is fully independent", lambda: deep["layers"] == [64, 32] and deep["layers"] is not config["layers"],
      "copy.deepcopy(config).")
check("You explained why shallow['layers'] changed", lambda: filled(var("WHY_SHALLOW_LAYERS_CHANGED"), 10))
check("You explained why shallow['lr'] did not", lambda: filled(var("WHY_SHALLOW_LR_DID_NOT"), 10))
