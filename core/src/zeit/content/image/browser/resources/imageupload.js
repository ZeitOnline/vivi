(function ($) {
  $(document).ready(function () {
    // Mimic core/src/zeit/content/article/edit/browser/resources/filename.js
    const form = document.querySelector('form[name="edit-images"]');
    if (!form) {
      return;
    }
    form.addEventListener('change', e => {
      if (e.target.name.startsWith('target_name[')) {
        e.target.value = zeit.cms.normalize_filename(e.target.value);
      }
    });

    form.addEventListener('click', e => {
      if (e.target.classList.contains('bulk-edit')) {
        const field = e.target.dataset.field;
        bulkEdit(field);
      }
    });

    function bulkEdit(field) {
      let promptMessage, currentValue = '';

      switch (field) {
        case 'filename': {
          promptMessage = 'Inhalt für alle Dateinamen überschreiben';
          // Get the base name from first filename (remove any existing suffix)
          let firstFilename = document.querySelector('input[name^="target_name["]').value;
          currentValue = firstFilename.replace(/-bild(-\d+)?$/, '');
          break;
        }
        case 'copyright':
          promptMessage = 'Copyright für alle überschreiben:';
          currentValue = document.querySelector('input[name^="copyright["]').value;
          break;
        case 'title':
          promptMessage = 'Titel für alle überschreiben:';
          currentValue = document.querySelector('textarea[name^="title["]').value;
          break;
        case 'caption':
          promptMessage = 'Bildunterschrift für alle überschreiben:';
          currentValue = document.querySelector('textarea[name^="caption["]').value;
          break;
      }

      const newValue = prompt(promptMessage, currentValue);
      if (newValue !== null) {
        applyBulkValue(field, newValue);
      }
    }

    function applyBulkValue(field, value) {
      if (field === 'filename') {
        applyBulkFilenames(value);
      } else {
        const inputs = document.querySelectorAll(`input[name^="${field}["], textarea[name^="${field}["]`);
        inputs.forEach(input => {
          input.value = value;
        });
      }
    }

    function applyBulkFilenames(baseName) {
      const inputs = document.querySelectorAll('input[name^="target_name["]');
      const normalizedBase = zeit.cms.normalize_filename(baseName);

      inputs.forEach((input, index) => {
        if (inputs.length === 1) {
          input.value = normalizedBase + '-bild';
        } else {
          input.value = normalizedBase + '-bild-' + String(index + 1).padStart(2, '0');
        }
      });
    }
  }); // End of document.ready
}(jQuery));
