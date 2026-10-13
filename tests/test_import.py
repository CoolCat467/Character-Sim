import character_sim


def test_has_run() -> None:
    assert hasattr(character_sim, "run")
    assert callable(character_sim.run)
