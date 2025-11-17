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
/*
// ----------------------
// ДОДАВАННЯ НОВИНИ
// ----------------------
document.getElementById('addNewsForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    data.images = data.images.split(',').map(img => img.trim());

    const res = await fetch('/add_news', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const result = await res.json();

    if (result.success) {
        bootstrap.Modal.getInstance(document.getElementById('addNewsModal')).hide();
        location.reload();
    } else {
        alert(result.error);
    }
});

// ----------------------
// РЕДАГУВАННЯ НОВИНИ
// ----------------------
document.querySelectorAll('.edit-news-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
        const id = btn.dataset.id;

        const res = await fetch(`/get_news/${id}`);
        const data = await res.json();

        if (data.success) {
            document.getElementById('editNewsId').value = id;
            document.getElementById('editNewsName').value = data.news.name;
            document.getElementById('editNewsDesc').value = data.news.description;
            document.getElementById('editNewsDesc2').value = data.news.descriptionSecond;
            document.getElementById('editNewsImages').value = data.news.images.join(', ');

            new bootstrap.Modal(document.getElementById('editNewsModal')).show();
        }
    });
});

document.getElementById('editNewsForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    data.images = data.images.split(',').map(i => i.trim());

    const res = await fetch(`/edit_news/${data.id}`, {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const result = await res.json();
    if (result.success) {
        bootstrap.Modal.getInstance(document.getElementById('editNewsModal')).hide();
        location.reload();
    } else {
        alert(result.error);
    }
});

// ----------------------
// ВИДАЛЕННЯ НОВИНИ
// ----------------------
document.querySelectorAll('.delete-news-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
        if (!confirm("Видалити новину?")) return;

        const id = btn.dataset.id;

        const res = await fetch(`/delete_news/${id}`, {
            method: 'DELETE'
        });

        const result = await res.json();

        if (result.success) {
            btn.closest('.list-group-item').remove();
        } else {
            alert(result.error);
        }
    });
}); */

document.getElementById('addNewsForm')?.addEventListener('submit', async function(e){
    e.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    data.images = data.images
        ? data.images.split(',').map(x => x.trim())
        : [];

    const response = await fetch('/add_news', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    const result = await response.json();

    if(result.success){
        bootstrap.Modal.getInstance(document.getElementById('addNewsModal')).hide();
        location.reload();
    } else {
        alert("Помилка");
    }
});

document.querySelectorAll('.edit-news-btn').forEach(btn => {
    btn.addEventListener('click', async function(){
        const id = this.dataset.id;

        const response = await fetch(`/get_news/${id}`);
        const result = await response.json();

        if(result.success){
            document.getElementById('editNewsId').value = id;
            document.getElementById('editNewsName').value = result.news.name;
            document.getElementById('editNewsDescription').value = result.news.description;
            document.getElementById('editNewsDescriptionSecond').value = result.news.descriptionSecond;
            document.getElementById('editNewsImages').value = result.news.images.join(', ');

            new bootstrap.Modal(document.getElementById('editNewsModal')).show();
        }
    });
});

document.getElementById('editNewsForm')?.addEventListener('submit', async function(e){
    e.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    data.images = data.images
        ? data.images.split(',').map(x => x.trim())
        : [];

    const response = await fetch(`/edit_news/${data.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    const result = await response.json();

    if(result.success){
        bootstrap.Modal.getInstance(document.getElementById('editNewsModal')).hide();
        location.reload();
    }
});

document.querySelectorAll('.delete-news-btn').forEach(btn => {
    btn.addEventListener('click', async function(){
        if(!confirm("Видалити новину?")) return;

        const id = this.dataset.id;

        const response = await fetch(`/delete_news/${id}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if(result.success) location.reload();
        else alert("Помилка при видаленні");
    });
});
    