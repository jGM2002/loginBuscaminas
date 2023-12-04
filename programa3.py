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
        messagebox.showinfo("Éxito", "Imagen cargada correctamente")


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
        jugadores_autenticados.append(result)
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


jugadores_autenticados = []


# Función para mostrar la información de un usuario en una ventana
def mostrarInformacionUsuario(usuario, row, col):
    id, nick, contrasenya, avatar, partides_jugades, partides_guanyades = usuario
    frameInfo = tk.Toplevel(ventanaPrincipal)
    frameInfo.configure(bg="#87CEEB")

    etiquetaNick = tk.Label(frameInfo, text=f'Nick: {nick}', bg="#87CEEB", fg="white")
    etiquetaNick.grid(row=row, column=col, padx=10, pady=10)
    etiquetaPartides = tk.Label(frameInfo, text=f'Partidas Jugadas: {partides_jugades}', bg="#87CEEB", fg="white")
    etiquetaPartides.grid(row=row + 1, column=col, padx=10, pady=10)
    etiquetaGuanyades = tk.Label(frameInfo, text=f'Partidas Ganadas: {partides_guanyades}', bg="#87CEEB", fg="white")
    etiquetaGuanyades.grid(row=row + 2, column=col, padx=10, pady=10)

    imagenAvatar = tk.Label(frameInfo, bg="#87CEEB")
    imagenAvatar.grid(row=3, column=0, pady=10, padx=10)

    botonMod = tk.Button(frameInfo, text="Modificar", command=lambda nick=nick: abrirSubfinestraModificar(nick), bg="#87CEEB", fg="white")
    botonMod.grid(row=4, column=2, padx=10, pady=10)

    botonEliminarUsuario = tk.Button(frameInfo, text="Eliminar usuario", command=lambda nick=nick: eliminarUsuario(nick), bg="#87CEEB", fg="white")
    botonEliminarUsuario.grid(row=5, column=2, pady=10, padx=10)

    cargarAvatar(nick, imagenAvatar)


# Función para abrir una ventana de modificación del usuario
def abrirSubfinestraModificar(nick):
    subventana = tk.Toplevel(ventanaPrincipal)
    subventana.title(f'Modificar Usuario: {nick}')
    subventana.configure(bg="#87CEEB")
    etiquetaNickMod = tk.Label(subventana, text='Nuevo Nick:', bg="#87CEEB", fg="white")
    etiquetaNickMod.grid(row=0, column=0)
    nuevaNickMod = tk.StringVar()
    entradaNickMod = tk.Entry(subventana, textvariable=nuevaNickMod)
    entradaNickMod.grid(row=0, column=1)
    entradaNickMod.insert(0, nick)

    etiquetaContrasenyaMod = tk.Label(subventana, text='Nueva Contraseña:', bg="#87CEEB", fg="white")
    etiquetaContrasenyaMod.grid(row=1, column=0)
    nuevaContrasenyaMod = tk.StringVar()
    entradaContrasenyaMod = tk.Entry(subventana, textvariable=nuevaContrasenyaMod, show='*')
    entradaContrasenyaMod.grid(row=1, column=1)

    etiquetaAvatarMod = tk.Label(subventana, text='Cambiar Avatar:', bg="#87CEEB", fg="white")
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
        cargarAvatar(nick, etiquetaAvatar)
        messagebox.showinfo("Éxito", "Imagen cargada correctamente")


# Función para actualizar el nick de un usuario
def actualizarNick(nickViejo, nickNuevo):
    if nickNuevo.strip() != "":
        cur.execute("UPDATE usuarios SET nick=? WHERE nick=?", (nickNuevo, nickViejo))
        conn.commit()
        messagebox.showinfo("Éxito", f"Nick actualizado a: {nickNuevo}")
    else:
        messagebox.showerror("Error", "El nuevo nick no puede estar vacío.")


# Función para actualizar la contraseña de un usuario
def actualizarContrasenya(nick, contrasenyaNueva):
    if contrasenyaNueva.strip() != "":
        cur.execute("UPDATE usuarios SET contrasenya=? WHERE nick=?", (contrasenyaNueva, nick))
        conn.commit()
        messagebox.showinfo("Éxito", "Contraseña actualizada")
    else:
        messagebox.showerror("Error", "La nueva contraseña no puede estar vacía.")


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
    cur.execute("INSERT INTO usuarios (nick, contrasenya, avatar, partides_jugades, partides_guanyades) VALUES (?, ?, ?, ?, ?)", (nick, contrasenya, avatar, 0, 0))
    conn.commit()
    messagebox.showinfo("Éxito", "Usuario registrado con éxito")


# Función para abrir la ventana de registro
def abrirVentanaRegistro():
    ventanaRegistro = tk.Toplevel(ventanaPrincipal)
    ventanaRegistro.title("Registro de Usuario")
    ventanaRegistro.configure(bg="#87CEEB")

    etiquetaNuevoNick = tk.Label(ventanaRegistro, text="Nuevo Nick:", bg="#87CEEB", fg="white")
    etiquetaNuevoNick.grid(row=0, column=0)
    nuevoNick = tk.StringVar()
    entradaNuevoNick = tk.Entry(ventanaRegistro, textvariable=nuevoNick)
    entradaNuevoNick.grid(row=0, column=1)

    etiquetaNuevaContrasenya = tk.Label(ventanaRegistro, text="Nueva Contraseña:", bg="#87CEEB", fg="white")
    etiquetaNuevaContrasenya.grid(row=1, column=0)
    nuevaContrasenya = tk.StringVar()
    entradaNuevaContrasenya = tk.Entry(ventanaRegistro, textvariable=nuevaContrasenya, show="*")
    entradaNuevaContrasenya.grid(row=1, column=1)

    etiquetaAvatar = tk.Label(ventanaRegistro, text="Avatar:", bg="#87CEEB", fg="white")
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

        jugador_seleccionado = seleccionarJugador(jugadores_autenticados)

        if jugador_seleccionado is not None:
            try:
                cur.execute("UPDATE usuarios SET partides_jugades = partides_jugades + 1 WHERE nick=?",
                                 (jugador_seleccionado,))
                conn.commit()
                print("Partidas jugadas actualizadas correctamente.")
            except Exception as e:
                print(f"Error al actualizar partidas jugadas: {e}")
            root = tk.Tk()
            game = programa2.Buscaminas(root, jugador_seleccionado)
            root.mainloop()


def cerrarVentana(ventana, valor):
    ventana.return_value = valor
    ventana.destroy()


# En lugar de utilizar una variable global, pasa la lista de jugadores autenticados como parámetro a la función
def seleccionarJugador(jugadores_autenticados):
    ventanaSeleccion = tk.Toplevel(ventanaPrincipal)
    ventanaSeleccion.title("Seleccionar Jugador")
    ventanaSeleccion.configure(bg="#87CEEB")

    etiquetaSeleccion = tk.Label(ventanaSeleccion, text="Selecciona el jugador que jugará la partida:", bg="#87CEEB", fg="white")
    etiquetaSeleccion.pack()

    jugador_seleccionado = tk.StringVar()

    for jugador in jugadores_autenticados:
        id, nick, _, _, _, _ = jugador
        botonJugador = tk.Button(ventanaSeleccion, text=f"jugador {nick}", command=lambda j=nick: jugador_seleccionado.set(j))
        botonJugador.pack()

    botonConfirmar = tk.Button(ventanaSeleccion, text="Confirmar", command=lambda: ventanaSeleccion.destroy())
    botonConfirmar.pack()

    ventanaSeleccion.wait_window()
    return jugador_seleccionado.get()


ventanaPrincipal = tk.Tk()
ventanaPrincipal.title("Juegos de Mesa con Usuarios")
ventanaPrincipal.configure(bg="#9370DB")

frameUsuario1 = tk.Frame(ventanaPrincipal, bg="#9370DB")
frameUsuario2 = tk.Frame(ventanaPrincipal, bg="#9370DB")

frameUsuario1.grid(row=0, column=0, padx=10, pady=10)
frameUsuario2.grid(row=0, column=1, padx=10, pady=10)

frameIngreso = tk.Frame(ventanaPrincipal, bg="#9370DB")
frameIngreso.grid(row=0, column=0, padx=10, pady=10)

frameJugador1 = tk.Frame(frameIngreso, bg="#9370DB")
frameJugador2 = tk.Frame(frameIngreso, bg="#9370DB")

frameJugador1.grid(row=0, column=0, padx=10, pady=10)
frameJugador2.grid(row=0, column=1, padx=10, pady=10)

intentos = 0

etiquetaNick1 = tk.Label(frameJugador1, text="Nick:", bg="#9370DB", fg="white")
etiquetaNick1.grid(row=0, column=0)
frameJugador1.nick = tk.StringVar()
entradaNick1 = tk.Entry(frameJugador1, textvariable=frameJugador1.nick, bg="#9370DB", fg="white")
entradaNick1.grid(row=0, column=1)

etiquetaContrasenya1 = tk.Label(frameJugador1, text="Contraseña:", bg="#9370DB", fg="white")
etiquetaContrasenya1.grid(row=1, column=0)
frameJugador1.contrasenya = tk.StringVar()
entradaContrasenya1 = tk.Entry(frameJugador1, textvariable=frameJugador1.contrasenya, show="*", bg="#9370DB", fg="white")
entradaContrasenya1.grid(row=1, column=1)

etiquetaNick2 = tk.Label(frameJugador2, text="Nick:", bg="#9370DB", fg="white")
etiquetaNick2.grid(row=0, column=0)
frameJugador2.nick = tk.StringVar()
entradaNick2 = tk.Entry(frameJugador2, textvariable=frameJugador2.nick, bg="#9370DB", fg="white")
entradaNick2.grid(row=0, column=1)

etiquetaContrasenya2 = tk.Label(frameJugador2, text="Contraseña:", bg="#9370DB", fg="white")
etiquetaContrasenya2.grid(row=1, column=0)
frameJugador2.contrasenya = tk.StringVar()
entradaContrasenya2 = tk.Entry(frameJugador2, textvariable=frameJugador2.contrasenya, show="*", bg="#9370DB", fg="white")
entradaContrasenya2.grid(row=1, column=1)

etiquetaAvatar = tk.Label(ventanaPrincipal, image=None)
nuevoAvatar = tk.StringVar()

botonRegistro = tk.Button(ventanaPrincipal, text="Registrarse", command=abrirVentanaRegistro)
botonRegistro.grid(row=2, column=1, padx=10, pady=10)

botonComenzar = tk.Button(ventanaPrincipal, text="Comenzar Partida", command=comprobarInicioPartida)
botonComenzar.grid(row=1, column=0, padx=10, pady=10)

ventanaPrincipal.mainloop()

conn.close()