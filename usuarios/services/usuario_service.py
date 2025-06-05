from usuarios.models import Usuario, Rol

def crear_usuario_con_rol(data):
    if 'rol' not in data or not data['rol']:
        try:
            rol_default = Rol.objects.get(nombre="Usuario General")
            data['rol'] = rol_default.id
        except Rol.DoesNotExist:
            raise ValueError("El rol por defecto no existe.")

    user = Usuario.objects.create_user(
        username=data['username'],
        email=data.get('email', ''),
        password=data['password'],
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', ''),
        is_staff=data.get('is_staff', False),
        is_active=data.get('is_active', True),
        is_superuser=data.get('is_superuser', False),
        rol_id=data['rol']
    )
    return user

def resetear_password(usuario, nueva_password='123'):
    usuario.set_password(nueva_password)
    usuario.save()
