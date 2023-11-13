import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import sqlite3
from PIL import Image, ImageTk
import programa2

conn = sqlite3.connect("usuarios.db")
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY,
        nick TEXT,
        contrasenya TEXT,
        avatar TEXT,
        partides_jugades INTEGER,
        partides_guanyades INTEGER
    )
""")
conn.commit()


# Función para abrir y cargar una imagen
def abrirImagen():
    filePath = filedialog.askopenfilename()
    if filePath:
        imagen = Image.open(filePath)
        imagen = imagen.resize((100, 100), Image.ANTIALIAS)
        imagen = ImageTk.PhotoImage(imagen)
        etiquetaAvatar.image = imagen
        etiquetaAvatar.configure(image=imagen)
        etiquetaAvatar.filePath = filePath


# Función para seleccionar un avatar
def seleccionarAvatar(nick):
    filaPath = filedialog.askopenfilename()
    if filaPath:
        nuevoAvatar.set(filaPath)


# Función para cargar el avatar de un usuario
def cargarAvatar(nick, etiquetaAvatar):
    cur.execute("SELECT avatar FROM usuarios WHERE nick=?", (nick,))
    result = cur.fetchone()
    if result and result[0]:
        imagen = Image.open(result[0])
        imagen.thumbnail((100, 100))
        imagen = ImageTk.PhotoImage(imagen)
        etiquetaAvatar.image = imagen
        etiquetaAvatar.configure(image=imagen)
        etiquetaAvatar.filePath = result[0]


# Función para autenticar a un usuario
def autenticarUsuario(frame, nick, contrasenya):
    cur.execute("SELECT id, nick, contrasenya, avatar, partides_jugades, partides_guanyades FROM usuarios WHERE nick=? AND contrasenya=?", (nick, contrasenya))
    result = cur.fetchone()
    if result:
        frame.destroy()
        if not frameUsuario1.winfo_ismapped():
            mostrarInformacionUsuario(result, 0, 0)
        else:
            mostrarInformacionUsuario(result, 0, 0)
    else:
        global intentos
        intentos += 1
        if intentos >= 3:
            messagebox.showerror("Error", "Demasiados intentos incorrectos. Saliendo del programa.")
            ventanaPrincipal.quit()


# Función para mostrar la información de un usuario en una ventana
def mostrarInformacionUsuario(usuario, row, col):
    id, nick, contrasenya, avatar, partides_jugades, partides_guanyades = usuario
    frameInfo = tk.Toplevel(ventanaPrincipal)

    etiquetaNick = tk.Label(frameInfo, text=f'Nick: {nick}')
    etiquetaNick.grid(row=row, column=col, padx=10, pady=10)
    etiquetaPartides = tk.Label(frameInfo, text=f'Partidas Jugadas: {partides_jugades}')
    etiquetaPartides.grid(row=row + 1, column=col, padx=10, pady=10)
    etiquetaGuanyades = tk.Label(frameInfo, text=f'Partidas Ganadas: {partides_guanyades}')
    etiquetaGuanyades.grid(row=row + 2, column=col, padx=10, pady=10)

    imagenAvatar = tk.Label(frameInfo)
    imagenAvatar.grid(row=3, column=0, pady=10, padx=10)

    botonMod = tk.Button(frameInfo, text="Modificar", command=lambda nick=nick: abrirSubfinestraModificar(nick))
    botonMod.grid(row=4, column=2, padx=10, pady=10)

    botonEliminarUsuario = tk.Button(frameInfo, text="Eliminar usuario", command=lambda nick=nick: eliminarUsuario(nick))
    botonEliminarUsuario.grid(row=5, column=2, pady=10, padx=10)

    cargarAvatar(nick, imagenAvatar)


# Función para abrir una ventana de modificación del usuario
def abrirSubfinestraModificar(nick):
    subventana = tk.Toplevel(ventanaPrincipal)
    subventana.title(f'Modificar Usuario: {nick}')
    etiquetaNickMod = tk.Label(subventana, text='Nuevo Nick:')
    etiquetaNickMod.grid(row=0, column=0)
    nuevaNickMod = tk.StringVar()
    entradaNickMod = tk.Entry(subventana, textvariable=nuevaNickMod)
    entradaNickMod.grid(row=0, column=1)
    entradaNickMod.insert(0, nick)

    etiquetaContrasenyaMod = tk.Label(subventana, text='Nueva Contraseña:')
    etiquetaContrasenyaMod.grid(row=1, column=0)
    nuevaContrasenyaMod = tk.StringVar()
    entradaContrasenyaMod = tk.Entry(subventana, textvariable=nuevaContrasenyaMod, show='*')
    entradaContrasenyaMod.grid(row=1, column=1)

    etiquetaAvatarMod = tk.Label(subventana, text='Cambiar Avatar:')
    etiquetaAvatarMod.grid(row=2, column=0)
    botonSeleccionarMod = tk.Button(subventana, text='Seleccionar Imagen', command=lambda: abrirImagenMod(nuevaNickMod.get()))
    botonSeleccionarMod.grid(row=2, column=1)

    botonActualizarNick = tk.Button(subventana, text='Actualizar Nick', command=lambda: actualizarNick(nick, nuevaNickMod.get()))
    botonActualizarNick.grid(row=3, column=0, padx=10, pady=10)
    botonActualizarContrasenya = tk.Button(subventana, text='Actualizar Contraseña', command=lambda: actualizarContrasenya(nick, nuevaContrasenyaMod.get()))
    botonActualizarContrasenya.grid(row=3, column=1, padx=10, pady=10)
    botonCerrarMod = tk.Button(subventana, text='Cerrar', command=subventana.destroy)
    botonCerrarMod.grid(row=4, column=0, columnspan=2)


# Función para abrir una ventana de selección de avatar para modificar
def abrirImagenMod(nick):
    filePath = filedialog.askopenfilename()
    if filePath:
        cur.execute("UPDATE usuarios SET avatar=? WHERE nick=?", (filePath, nick))
        conn.commit()
        cargarAvatar(nick)


# Función para actualizar el nick de un usuario
def actualizarNick(nickViejo, nickNuevo):
    cur.execute("UPDATE usuarios SET nick=? WHERE nick=?", (nickNuevo, nickViejo))
    conn.commit()
    messagebox.showinfo("Éxito", f"Nick actualizado a: {nickNuevo}")


# Función para actualizar la contraseña de un usuario
def actualizarContrasenya(nick, contrasenyaNueva):
    cur.execute("UPDATE usuarios SET contrasenya=? WHERE nick=?", (contrasenyaNueva, nick))
    conn.commit()
    messagebox.showinfo("Éxito", "Contraseña actualizada")


# Función para eliminar un usuario
def eliminarUsuario(nick):
    cur.execute("DELETE FROM usuarios WHERE nick=?", (nick,))
    conn.commit()
    messagebox.showinfo("Éxito", "Usuario eliminado")
    mostrarFrameIngreso()


# Función para mostrar el frame de ingreso
def mostrarFrameIngreso():
    global intentos
    frameIngreso.grid(row=3, column=0, padx=10, pady=10)
    intentos = 0


# Función para registrar un nuevo usuario
def registrarUsuario(nick, contrasenya, avatar):
    cur.execute("INSERT INTO usuarios (nick, contrasenya, avatar) VALUES (?, ?, ?)", (nick, contrasenya, avatar))
    conn.commit()
    messagebox.showinfo("Éxito", "Usuario registrado con éxito")


# Función para abrir la ventana de registro
def abrirVentanaRegistro():
    ventanaRegistro = tk.Toplevel(ventanaPrincipal)
    ventanaRegistro.title("Registro de Usuario")

    etiquetaNuevoNick = tk.Label(ventanaRegistro, text="Nuevo Nick:")
    etiquetaNuevoNick.grid(row=0, column=0)
    nuevoNick = tk.StringVar()
    entradaNuevoNick = tk.Entry(ventanaRegistro, textvariable=nuevoNick)
    entradaNuevoNick.grid(row=0, column=1)

    etiquetaNuevaContrasenya = tk.Label(ventanaRegistro, text="Nueva Contraseña:")
    etiquetaNuevaContrasenya.grid(row=1, column=0)
    nuevaContrasenya = tk.StringVar()
    entradaNuevaContrasenya = tk.Entry(ventanaRegistro, textvariable=nuevaContrasenya, show="*")
    entradaNuevaContrasenya.grid(row=1, column=1)

    etiquetaAvatar = tk.Label(ventanaRegistro, text="Avatar:")
    etiquetaAvatar.grid(row=2, column=0)
    botonSeleccionarAvatar = tk.Button(ventanaRegistro, text="Seleccionar Avatar", command=lambda: seleccionarAvatar(nuevoNick.get()))
    botonSeleccionarAvatar.grid(row=2, column=1)

    botonRegistrar = tk.Button(ventanaRegistro, text="Registrar", command=lambda: registrarUsuario(nuevoNick.get(), nuevaContrasenya.get(), nuevoAvatar.get()))
    botonRegistrar.grid(row=3, column=0, columnspan=2)


# Función que comprueba los usuarios e inicia la partida
def comprobarInicioPartida():
    if len(frameJugador1.nick.get()) == 0 or len(frameJugador2.nick.get()) == 0:
        messagebox.showerror("Error", "Debes ingresar los nicks de ambos jugadores.")
    else:
        autenticarUsuario(frameJugador1, frameJugador1.nick.get(), frameJugador1.contrasenya.get())
        autenticarUsuario(frameJugador2, frameJugador2.nick.get(), frameJugador2.contrasenya.get())
        programa2.iniciarPartida()


ventanaPrincipal = tk.Tk()
ventanaPrincipal.title("Juegos de Mesa con Usuarios")

frameUsuario1 = tk.Frame(ventanaPrincipal)
frameUsuario2 = tk.Frame(ventanaPrincipal)

frameUsuario1.grid(row=0, column=0, padx=10, pady=10)
frameUsuario2.grid(row=0, column=1, padx=10, pady=10)

frameIngreso = tk.Frame(ventanaPrincipal)
frameIngreso.grid(row=0, column=0, padx=10, pady=10)

frameJugador1 = tk.Frame(frameIngreso)
frameJugador2 = tk.Frame(frameIngreso)

frameJugador1.grid(row=0, column=0, padx=10, pady=10)
frameJugador2.grid(row=0, column=1, padx=10, pady=10)

intentos = 0

etiquetaNick1 = tk.Label(frameJugador1, text="Nick:")
etiquetaNick1.grid(row=0, column=0)
frameJugador1.nick = tk.StringVar()
entradaNick1 = tk.Entry(frameJugador1, textvariable=frameJugador1.nick)
entradaNick1.grid(row=0, column=1)

etiquetaContrasenya1 = tk.Label(frameJugador1, text="Contraseña:")
etiquetaContrasenya1.grid(row=1, column=0)
frameJugador1.contrasenya = tk.StringVar()
entradaContrasenya1 = tk.Entry(frameJugador1, textvariable=frameJugador1.contrasenya, show="*")
entradaContrasenya1.grid(row=1, column=1)

etiquetaNick2 = tk.Label(frameJugador2, text="Nick:")
etiquetaNick2.grid(row=0, column=0)
frameJugador2.nick = tk.StringVar()
entradaNick2 = tk.Entry(frameJugador2, textvariable=frameJugador2.nick)
entradaNick2.grid(row=0, column=1)

etiquetaContrasenya2 = tk.Label(frameJugador2, text="Contraseña:")
etiquetaContrasenya2.grid(row=1, column=0)
frameJugador2.contrasenya = tk.StringVar()
entradaContrasenya2 = tk.Entry(frameJugador2, textvariable=frameJugador2.contrasenya, show="*")
entradaContrasenya2.grid(row=1, column=1)

etiquetaAvatar = tk.Label(ventanaPrincipal, image=None)
nuevoAvatar = tk.StringVar()

botonRegistro = tk.Button(ventanaPrincipal, text="Registrarse", command=abrirVentanaRegistro)
botonRegistro.grid(row=2, column=1, padx=10, pady=10)

botonComenzar = tk.Button(ventanaPrincipal, text="Comenzar Partida", command=comprobarInicioPartida)
botonComenzar.grid(row=1, column=0, padx=10, pady=10)

ventanaPrincipal.mainloop()

conn.close()