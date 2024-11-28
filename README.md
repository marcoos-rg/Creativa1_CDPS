# Creativa 1

**Creativa 1** es un proyecto desarrollado como parte de la asignatura **CDPS** (*Composición de Despliegues y Servicios*) impartida en la **Universidad Politécnica de Madrid (UPM)**. Este proyecto simula un entorno de máquinas virtuales conectadas a redes virtuales utilizando herramientas como **libvirt** y **Open vSwitch**, gestionadas a través de un conjunto de comandos personalizados.

---

## Autores

- **Guillermo Peláez Cañizares** - [@GuillePc](https://github.com/GuillePc)
- **Marcos Rosado González** - [@marcoos-rg](https://github.com/marcoos-rg)

---

## Funcionalidad

El proyecto permite gestionar un entorno de redes y máquinas virtuales con los siguientes comandos:

### Comandos Disponibles

| Comando                          | Descripción                                                                                   |
|----------------------------------|-----------------------------------------------------------------------------------------------|
| `create <num_servers>`           | Crea la red y el número especificado de servidores.                                           |
| `start (<server_name>)`      | Arranca todas las máquinas virtuales o una específica.                                        |
| `stop (<server_name>)`       | Detiene todas las máquinas virtuales o una específica.                                        |
| `destroy`                        | Elimina todas las máquinas y redes configuradas.                                              |
| `monitor (<server_name>)`                          | Muestra el estado actual de todas las máquinas virtuales (basado en `virsh domstate`).        |
| `info (<server_name>)`           | Muestra información detallada de una máquina virtual específica o de todas (basado en `virsh dominfo`). |
| `help`                           | Muestra la lista de comandos disponibles y su funcionalidad.                                  |

---

## Requisitos

### Dependencias del Sistema

1. **Python 3.x** (incluye `subprocess` y `logging`)
2. **libvirt**:
   - Instalar con:
     ```bash
     sudo apt install libvirt-clients libvirt-daemon-system
     ```
3. **Open vSwitch**:
   - Instalar con:
     ```bash
     sudo apt install openvswitch-switch
     ```
4. **Permisos de `sudo`**:
   - El script requiere acceso a comandos como `virsh` y `ovs-vsctl`, que necesitan permisos de superusuario.

---

## Uso

### 1. **Clonar el Repositorio**:
   ```bash
   git clone https://github.com/marcoos-rg/Creativa1_CDPS.git
   cd Creativa1_CDPS
  ```
### 2. **Editar el Archivo `manage-p2.json`:**

Configura el número inicial de servidores y el modo de depuración. Por ejemplo:
```json
{
    "number_of_servers": 3,
    "debug": true
}
```
### 3. **Ejecutar Comandos:**
* **Crear un entorno con 5 servidores:**
  ```bash
   python3 manage-p2.py create 5
  ```
* **Arrancar las maquinas virtuales:**
  ```bash
   python3 manage-p2.py start
  ```
* **Ver el estado de las maquinas virtuales:**
  ```bash
   python3 manage-p2.py state
  ```
### 4. **Ayuda:**
* Para obtener la lista completa de comandos: 
```bash
   python3 manage-p2.py help
  ```
