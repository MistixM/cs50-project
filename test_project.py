import project_server, project_client
import customtkinter

# Server part
def test_status():
    assert project_server.get_status(True) == True
    assert project_server.get_status(False) == False

def test_connection():
    assert project_server.is_connect('localhost', 2424) == True
    assert project_server.is_connect('localhost', 0000) == True

# Client part
def test_client_receive():
    # Suppose that we have receive func here
    assert project_client.get_receive(True) == True
    assert project_client.get_receive(False) == False

def test_client_ui():
    app = customtkinter.CTk()
    app.geometry("389x389")
    app.title("Join chat")

    assert project_client.check_gui(app._get_window_scaling(), app.title) == True
    assert project_client.check_gui(None, None) == False