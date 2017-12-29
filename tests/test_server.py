def setup_module(module):
    global server
    from mafiservo import server


def test_new_game_id():
    for g in range(1, 10):
        g_id = server.new_game_id()
        assert 10 < g_id < 100
        server.games[g_id] = g_id
    for g in range(11, 100):
        g_id = server.new_game_id()
        assert 100 < g_id < 1000
        server.games[g_id] = g_id
