document.getElementById('addItemForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/add_item', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if(result.success) {
            // Закриваємо модалку
            const addItemModal = bootstrap.Modal.getInstance(document.getElementById('addItemModal'));
            addItemModal.hide();

            // Перезавантажуємо сторінку, щоб оновити список товарів
            location.reload();
        } else {
            alert(result.error || "Помилка при додаванні товару");
        }

    } catch (err) {
        console.error(err);
        alert("Помилка при відправці форми");
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const editForm = document.getElementById('editItemForm');
    if (!editForm) return;

    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const itemId = this.dataset.id;
            const response = await fetch(`/get_item/${itemId}`);
            const data = await response.json();

            if(data.success){
                document.getElementById('editItemId').value = itemId;
                document.getElementById('editItemName').value = data.item.name;
                document.getElementById('editItemDescription').value = data.item.description;
                document.getElementById('editItemPrice').value = data.item.price;
                document.getElementById('editItemImage').value = data.item.image;

                const editModal = new bootstrap.Modal(document.getElementById('editItemModal'));
                editModal.show();
            }
        });
    });

    editForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const data = Object.fromEntries(formData.entries());

        const response = await fetch(`/edit_item/${data.id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if(result.success){
            const modal = bootstrap.Modal.getInstance(document.getElementById('editItemModal'));
            modal.hide();
            location.reload();
        } else {
            alert(result.error || "Помилка");
        }
    });
});

document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', async function () {

        if (!confirm("Видалити товар?")) return;

        const id = this.dataset.id;

        const response = await fetch(`/delete_item/${id}`, {
            method: 'DELETE',
            headers: {
                "Content-Type": "application/json"
            }
        });

        const result = await response.json();

        if (result.success) {
            this.closest('.col-md-4').remove();
        } else {
            alert(result.error || "Помилка при видаленні!");
        }
    });
});

