(function ($) {
  $(document).ready(function () {
    const form = document.querySelector('form[name="imageupload"]');
    if (!form) {
      return;
    }
    class UserFile {
      #file

      constructor(file) {
        this.#file = file
      }

      data() {
        return this.#file
      }

      filename() {
        return this.#file.name
      }

      async thumbnail() {
        return new Promise(resolve => {
          let reader = new FileReader()
          reader.readAsDataURL(this.#file)
          reader.onloadend = () => resolve(reader.result)
        });
      }
    }

    class MDBFile {
      #id
      #filename
      #thumbnail

      constructor(id, filename, thumbnail) {
        this.#id = id
        this.#filename = filename
        this.#thumbnail = thumbnail
      }

      data() {
        return 'mdb:' + this.#id
      }

      filename() {
        return this.#filename
      }

      async thumbnail() {
        return this.#thumbnail
      }
    }

    class ImageUpload {
      #form
      #dropArea
      #gallery
      #submitButton

      constructor(form) {
        this.#form = form
        this.#dropArea = form.querySelector('.imageupload__drop')
        this.#gallery = form.querySelector('.imageupload__gallery')
        this.#submitButton = form.querySelector('.imageupload__button--submit')

        this.#dropArea.addEventListener('dragenter', this, false)
        this.#dropArea.addEventListener('dragover', this, false)
        this.#dropArea.addEventListener('dragleave', this, false)
        this.#dropArea.addEventListener('drop', this, false)
        form.querySelector('[type="file"]').addEventListener('change', this, false)
        form.querySelector('.imageupload__button--add-mdb-ids').addEventListener('click', this, false)
        this.#gallery.addEventListener('click', this, false)
        this.#submitButton.addEventListener('click', this, false)
      }

      handleEvent(e) {
        switch (e.type) {
          case 'dragenter':
            this.#dropArea.classList.add('imageupload__drop--active')
            e.preventDefault()
            e.stopPropagation()
            break
          case 'drop':
            this.handleDrop(e.dataTransfer)
            this.#dropArea.classList.remove('imageupload__drop--active')
            e.preventDefault()
            e.stopPropagation()
            break
          case 'dragleave':
            this.#dropArea.classList.remove('imageupload__drop--active')
            e.preventDefault()
            e.stopPropagation()
            break
          case 'dragover':
            e.preventDefault()
            e.stopPropagation()
            break
          case 'change':
            this.handleFiles(e.target.files)
            break
          case 'click':
            if (e.target == this.#submitButton) {
              e.preventDefault()
              this.uploadFiles()
            } else if (e.target.classList.contains('imageupload__button--remove')) {
              const li = e.target.closest('li')
              this.removeFile(li)
            } else if (e.target.classList.contains('imageupload__button--add-mdb-ids')) {
              e.preventDefault()
              this.handleMdbInput(this.#form.querySelector('.imageupload__mdb-ids'))
            }
            break
        }
      }

      async handleMdbInput(input) {
        const newValues = []
        const ids = input.value.split(/\s*,\s*/).filter(s => s)
        for (let id of ids) {
          try {
            const metadata = await zeit.content.image.get_mdb_metadata(id)
            this.addFile(new MDBFile(metadata['mdb_id'], metadata['filename'], ""))
          } catch (e) {
            newValues.push(id)
          }
        }
        input.value = newValues.join(', ')
      }

      handleDrop(dataTransfer) {
        if (dataTransfer.files.length) {
          this.handleFiles(dataTransfer.files)
        } else {
          try {
            for (const { mdb_id, thumb, file_name } of zeit.content.image.parse_mdb_drop(dataTransfer)) {
              this.addFile(new MDBFile(mdb_id, file_name, thumb))
            }
          } catch (error) {
            alert(error)
          }
        }
      }

      handleFiles(files) {
        for (let file of files) {
          this.addFile(new UserFile(file))
        }
      }

      addFile(file, file_name, thumbnail_promise) {
        const li = this.#form.querySelector('.imageupload__template').content.cloneNode(true).firstElementChild
        li.querySelector('.imageupload__filename').textContent = file.filename()
        li.upload_data = file.data()
        file.thumbnail().then(thumbnail => {
          const img = li.querySelector('img')
          img.onerror = () => img.src = '/fanstatic/zeit.cms/preview_not_available.png'
          img.src = thumbnail
        })
        this.#gallery.appendChild(li)
      }

      removeFile(li) {
        li.remove()
      }

      async uploadFiles() {
        this.#form.classList.add('imageupload--uploading')
        this.#submitButton.disabled = true
        const uploads = []

        for (let li of this.#gallery.childNodes) {
          const errorSpan = li.querySelector('.imageupload__error')
          errorSpan.textContent = ''

          try {
            const url = await this.uploadFile(li.upload_data, progress => {
              li.querySelector('progress').value = progress
            })
            uploads.push(url)
          } catch (error) {
            errorSpan.textContent = error.message || error
          }
        }

        this.#form.classList.remove('imageupload--uploading')
        this.#submitButton.disabled = false

        if (!uploads.length) {
          return
        }

        const baseUrl = uploads[0]
        const additionalFiles = uploads.slice(1).map(url => {
          return '&files=' + new URL(url).searchParams.get('files')
        }).join('')

        const url = baseUrl + additionalFiles
        window.location = url
      }

      uploadFile(file, updateProgress) {
        return new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest()
          xhr.open('POST', this.#form.action, true)
          xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest')

          xhr.upload.addEventListener("progress", function (e) {
            updateProgress((e.loaded * 100.0 / e.total) || 100)
          })

          xhr.addEventListener('readystatechange', function (e) {
            if (xhr.readyState == 4 && xhr.status == 200) {
              updateProgress(100)
              resolve(xhr.responseText)
            }
            else if (xhr.readyState == 4 && xhr.status != 200) {
              reject(xhr.responseText || 'Unbekannter Fehler')
            }
          })

          const formData = new FormData()
          formData.append('files', file)
          xhr.send(formData)
        })
      }
    }

    new ImageUpload(document.querySelector('.imageupload'));

  }); // End of document.ready
}(jQuery));
