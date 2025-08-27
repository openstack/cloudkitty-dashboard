const groupbyList = JSON.parse(document.getElementById(
    'groupby_list_config').textContent);
const translations = JSON.parse(document.getElementById(
    'groupby_translations').textContent);

class GroupByManager {
constructor() {
    this.groupby = groupbyList || ['type'];
    this.checkboxContainer = document.getElementById('checkboxes');
    this.urlParams = new URLSearchParams(window.location.search);
    this.form = document.getElementById('groupby_checkbox');
    this.toggleButton = document.getElementById('toggleAll');

    this.init();
}

// Convert field names to readable format
formatLabel(word) {
    return word.replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase())
    .replace(/\bId\b/g, 'ID');
}

// Create checkbox with label
createCheckbox(name) {
    const label = document.createElement('label');
    label.className = 'group-label';
    label.innerHTML = `
    <input type="checkbox" name="${name}" id="checkbox-${name}"
            value="true" class="group-checkbox">
    ${this.formatLabel(name)}
    `;
    return label;
}

// Determine checkbox state from URL params or session storage
getCheckboxState(name) {
    if (this.urlParams.has(name)) {
    return this.urlParams.get(name) === 'true';
    }

    if (this.urlParams.toString()) {
    return false; // URL has params but not this one
    }

    //if we have a saved state use it, otherwise default to type checked
    const saved = sessionStorage.getItem(`checkbox-${name}`);
    return saved !== null ? saved === 'true' : name === 'type';
}

// Set up all checkboxes
setupCheckboxes() {
    let shouldAutoSubmit = false;

    this.groupby.forEach(name => {
    const label = this.createCheckbox(name);
    const checkbox = label.querySelector('input');

    checkbox.checked = this.getCheckboxState(name);

    if (checkbox.checked && !this.urlParams.toString()) {
        shouldAutoSubmit = true;
    }

    // Save state and add listener
    sessionStorage.setItem(`checkbox-${name}`, checkbox.checked);
    checkbox.addEventListener('change', () => {
        sessionStorage.setItem(`checkbox-${name}`, checkbox.checked);
        this.updateToggleButton();
    });

    this.checkboxContainer.appendChild(label);
    });

    if (shouldAutoSubmit) {
    this.form.submit();
    }
}

// Update toggle button text based on current state
updateToggleButton() {
    const checkboxes = this.checkboxContainer.querySelectorAll('.group-checkbox');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    this.toggleButton.textContent = allChecked ?
    translations.unselect_all : translations.select_all;
}

// Toggle all checkboxes
toggleAll() {
    const checkboxes = this.checkboxContainer.querySelectorAll('.group-checkbox');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);

    checkboxes.forEach(cb => {
    cb.checked = !allChecked;
    sessionStorage.setItem(`checkbox-${cb.name}`, cb.checked);
    });

    this.updateToggleButton();
    this.form.submit();
}

// Initialize the component
init() {
    this.setupCheckboxes();
    this.updateToggleButton();
    this.toggleButton.addEventListener('click', () => this.toggleAll());
}
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => new GroupByManager());
