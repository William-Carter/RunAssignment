from database.Interface import Interface

db = Interface("veri.db")

verifiers = [
    [
        "237052911551512576", "halosnow"
    ],
    [
        "556158163280330754", "griddo"
    ],
    [
        "612310109825269797", "evanlin"
    ],
    [
        "721383838122639360", "kale"
    ],
    [
        "776257321780248596", "knightednave"
    ],
    [
        "836238555482816542", "alatreph"
    ],
]


for verifier in verifiers:
    db.insertAndFetchRowID(
        """
        INSERT INTO Verifiers (discordId, name, srcId, weeklyMessageReceived, isActive, isAdmin)
        VALUES (?, ?, ?, 0, 1, 0)
        """,
        (verifier[0], verifier[1], verifier[1])
    )