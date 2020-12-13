function confSubmit(form, message) {
    if (confirm(message)) {
        form.submit();
    }
}
