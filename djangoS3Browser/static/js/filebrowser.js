var dropZone = document.getElementById('drop-zone');
var uploadForm = document.getElementById('js-upload-form');
var selected_file_list = [];
var copy_selected_file_list = [];
var sort_a_z_value = true;
var current_bucket = $('#bucket').attr("data-bucket");

function showToast(message, type) {
    var cls = type === 'error' ? 'alert-danger' : 'alert-success';
    var toast = $('<div class="alert ' + cls + ' alert-dismissible" role="alert">' +
        '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
        message +
        '</div>');
    $('#toast-container').append(toast);
    setTimeout(function () {
        toast.alert('close');
    }, 4000);
}

function humanSize(bytes) {
    if (bytes === null || bytes === undefined) return '-';
    var thresh = 1024;
    if (Math.abs(bytes) < thresh) {
        return bytes + ' B';
    }
    var units = ['KB', 'MB', 'GB', 'TB'];
    var u = -1;
    do {
        bytes /= thresh;
        ++u;
    } while (Math.abs(bytes) >= thresh && u < units.length - 1);
    return bytes.toFixed(1) + ' ' + units[u];
}

function renderBreadcrumb(loc) {
    var crumb = $('#breadcrumb');
    var html = '<ol class="breadcrumb">';
    html += '<li><a href="javascript:;" onclick="get_files(\'-\');">Home</a></li>';
    if (loc !== '-') {
        var parts = loc.slice(1).split('/').filter(function (p) { return p.length > 0; });
        var path = '-';
        for (var i = 0; i < parts.length; i++) {
            path += parts[i] + '/';
            if (i === parts.length - 1) {
                html += '<li class="active">' + parts[i] + '</li>';
            } else {
                html += '<li><a href="javascript:;" onclick="get_files(\'' + path + '\');">' + parts[i] + '</a></li>';
            }
        }
    }
    html += '</ol>';
    crumb.html(html);
}

function startUpload(files) {
    var loc = $('#location').attr("data-location");
    var bucket = $('#bucket').attr("data-bucket");
    $.each(files, function (key, file) {
        $.ajax({
            url: UPLOAD_URL,
            type: 'POST',
            dataType: 'json',
            data: {
                file_name: file.name,
                loc: loc,
                content_type: file.type,
                bucket: bucket
            },
            success: function (presignData) {
                var formData = new FormData();
                $.each(presignData.fields, function (fieldKey, fieldValue) {
                    formData.append(fieldKey, fieldValue);
                });
                formData.append("file", file);
                $.ajax({
                    xhr: function () {
                        var xhr = new window.XMLHttpRequest();
                        xhr.upload.addEventListener("progress", function (evt) {
                            if (evt.lengthComputable) {
                                var percentComplete = (evt.loaded / evt.total * 100 | 0);
                                var progress_bar = document.getElementById("progress-bar");
                                var progress_bar_rate = document.getElementById("progress-bar-rate");
                                progress_bar.style.width = percentComplete + '%';
                                progress_bar_rate.innerHTML = percentComplete + ' % ' + file.name;
                            }
                        }, false);
                        return xhr;
                    },
                    url: presignData.url,
                    contentType: false,
                    type: 'POST',
                    processData: false,
                    data: formData,
                    success: function () {
                        document.getElementById("js-upload-finished-list").innerHTML += '<a href="#" ' +
                            'class="list-group-item list-group-item-success">' +
                            SUCCESS_MSG + file.name + '</a>';
                        showToast('Uploaded ' + file.name, 'success');
                        get_files(loc);
                    },
                    error: function () {
                        document.getElementById("js-upload-finished-list").innerHTML += '<a href="#" ' +
                            'class="list-group-item list-group-item-danger">' +
                            FAIL_MSG + file.name + '</a>';
                        showToast('Upload failed for ' + file.name, 'error');
                    }
                });
            },
            error: function () {
                document.getElementById("js-upload-finished-list").innerHTML += '<a href="#" ' +
                    'class="list-group-item list-group-item-danger">' +
                    FAIL_MSG + file.name + '</a>';
                showToast('Upload failed for ' + file.name, 'error');
            }
        });
    })
}

if (uploadForm) {
    uploadForm.addEventListener('submit', function (e) {
        var uploadFiles = document.getElementById('js-upload-files').files;
        e.preventDefault();
        startUpload(uploadFiles);
    });
}

if (dropZone) {
    dropZone.ondrop = function (e) {
        e.preventDefault();
        this.className = 'upload-drop-zone';
        startUpload(e.dataTransfer.files)
    };

    dropZone.ondragover = function () {
        this.className = 'upload-drop-zone drop';
        return false;
    };

    dropZone.ondragleave = function () {
        this.className = 'upload-drop-zone';
        return false;
    };
}

$(document).ready(function () {
    renderBreadcrumb("-");
    get_files("-");
});

function change_bucket(select) {
    current_bucket = select.value;
    $('#bucket').attr("data-bucket", current_bucket);
    get_files("-");
}

function create_folder() {
    var loc = $('#location').attr("data-location");
    var folder_name = $('#created_folder_name').val();
    data = {"folder_name": folder_name, 'loc': loc, 'bucket': current_bucket};
    $.ajax({
        url: CREATE_FOLDER_URL,
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function () {
            showToast('Folder created', 'success');
        }
    });
    $('#collapseCreateFolder').collapse("hide");
    get_files(loc);
}

function sort_a_z(d) {
    loc = $('#location').attr("data-location");
    $(d).find('span').toggleClass('fa-sort-alpha-desc');
    if ($(d).attr("data-sort") === "a-z") {
        $(d).attr("data-sort", "z-a");
        sort_a_z_value = false;
    } else {
        $(d).attr("data-sort", "a-z");
        sort_a_z_value = true;
    }
    get_files(loc);
}

function clear_selection() {
    selected_file_list = [];
    copy_selected_file_list = [];
    $('#paste_file').addClass('hidden');
    $('#move_file').addClass('hidden');
    $('.file-row').removeClass('info');
    $('.file-check').prop('checked', false);
}

function toggle_row_selection(row) {
    var key = $(row).attr('data-key');
    if ($(row).hasClass('info')) {
        $(row).removeClass('info');
        selected_file_list.splice(selected_file_list.indexOf(key), 1);
        $(row).find('.file-check').prop('checked', false);
    } else {
        $(row).addClass('info');
        selected_file_list.push(key);
        $(row).find('.file-check').prop('checked', true);
    }
}

function copy_selected_file() {
    copy_selected_file_list = selected_file_list.slice();
    if (copy_selected_file_list.length > 0) {
        $('#paste_file').removeClass('hidden');
        $('#move_file').removeClass('hidden');
    }
}


function paste_file() {
    loc = $('#location').attr("data-location");
    $('#paste_file').toggleClass('hidden');
    $('#move_file').toggleClass('hidden');
    data = {'loc': loc, 'file_list': copy_selected_file_list, 'bucket': current_bucket};
    $.ajax({
        url: PAST_FILE_URL,
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (resultData) {
            copy_selected_file_list = [];
            showToast('Pasted items', 'success');
            get_files(loc);
        },
    });
}


function delete_file() {
    loc = $('#location').attr("data-location");
    data = {'file_list': selected_file_list, 'bucket': current_bucket};
    $.ajax({
        url: DELETE_FILE_URL,
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (resultData) {
            showToast('Deleted items', 'success');
            get_files(loc);
        },
    });
}


function refresh_folder() {
    get_files($('#location').attr("data-location"));
}

function open_item(d) {
    var keyValue = $(d).attr("data-key");
    url = d.getAttribute("data-url");
    type = d.getAttribute("data-type");
    if (type === 'folder') {
        get_files(keyValue);
    } else {
        $.getJSON(DOWNLOAD_URL, {file: keyValue, bucket: current_bucket}, function (data) {
            if (data.url) {
                window.open(data.url, '_blank');
            }
        });
    }
}

function back_folder(d) {
    var loc = d.getAttribute('data-top_folder');
    get_files(loc);
    $('#location').attr("data-location", loc);
    var top_loc = "";
    var loc_array = loc.split('/');
    for (var i = 0; i < loc_array.length - 2; i++) {
        top_loc = top_loc + loc_array[i] + "/"
    }
    if (1 > top_loc.length) {
        top_loc = "-"
    }
    $('#top_folder').attr("data-top_folder", top_loc);
}

function get_files(main_folder) {
    selected_file_list = [];
    $('#top_folder').attr("data-top_folder", $('#location').attr("data-location"));
    $('#location').attr("data-location", main_folder);
    renderBreadcrumb(main_folder);
    var tbody = $(".pb-filemng-template-body");
    tbody.empty();
    $("#empty-folder-msg").addClass('hidden');
    var get_files_url = FILES_URL.replace(/arg1djs3server/, main_folder.toString()).replace(/sort_a_z/, sort_a_z_value);
    get_files_url = get_files_url + "?bucket=" + encodeURIComponent(current_bucket);
    $.getJSON(
        get_files_url, function (files_list) {
            if (files_list.length === 0) {
                $("#empty-folder-msg").removeClass('hidden');
            }
            for (var key in files_list) {
                var displayName = files_list[key].text;
                var fullKey = files_list[key].full_key || (main_folder + files_list[key].text);
                var typeLabel = files_list[key].type === 'folder' ? 'Folder' : 'File';
                var sizeText = files_list[key].size !== null ? humanSize(files_list[key].size) : '-';
                var modifiedText = files_list[key].last_modified ? new Date(files_list[key].last_modified).toLocaleString() : '-';
                var row = $('<tr class="file-row" data-key="' + fullKey + '" data-type="' + files_list[key].type + '" data-url="' + files_list[key].url + '">' +
                    '<td><input type="checkbox" class="file-check"/></td>' +
                    '<td><img src="' + files_list[key].icon + '" class="icon-thumb"/> ' + displayName + '</td>' +
                    '<td>' + typeLabel + '</td>' +
                    '<td>' + sizeText + '</td>' +
                    '<td>' + modifiedText + '</td>' +
                    '</tr>');
                row.on('click', function (e) {
                    if (e.target && e.target.classList.contains('file-check')) {
                        toggle_row_selection(this);
                        e.stopPropagation();
                    } else {
                        toggle_row_selection(this);
                    }
                });
                row.on('dblclick', function () {
                    open_item(this);
                });
                tbody.append(row);
            }
        });
}

function download_files() {
    for (var key in selected_file_list) {
        $.getJSON(DOWNLOAD_URL, {file: selected_file_list[key], bucket: current_bucket}, function (data) {
            if (data.url) {
                window.open(data.url, "_blank");
            }
        });
    }
}

function rename_file_onfocus(d) {
    $(d).parent().find('.rename-input').removeClass('hidden');
    $(d).parent().find('.rename-input').focus();
    $(d).toggleClass('hidden');
}

function rename_file_onfocusout(d) {
    var file = $(d).parent().find('.pb-filemng-paragraphs').html();
    var loc = $('#location').attr("data-location");
    var new_name = $(d).val();
    data = {'loc': loc, 'file': file, 'new_name': new_name, 'bucket': current_bucket};
    $.ajax({
        url: RENAME_URL,
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (resultData) {
            $(d).parent().find('.pb-filemng-paragraphs').html(resultData);
            $(d).parent().find('.pb-filemng-paragraphs').removeClass('hidden');
            $(d).toggleClass('hidden');
        },
    });
}

function move_file(loc, file_list) {
    $('#move_file').toggleClass('hidden');
    $('#paste_file').toggleClass('hidden');
    data = {'loc': loc, 'file_list': file_list, 'bucket': current_bucket};
    $.ajax({
        url: MOVE_FILE_URL,
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (resultData) {
            get_files($('#location').attr("data-location"));
        },
    });
}


function move_selected_file(d) {
    move_file($('#location').attr("data-location"), copy_selected_file_list);
}

function dragstart_file(e) {
    for (var key in selected_file_list) {
        $("tr[data-key=\"" + selected_file_list[key] + "\"]")[0].style.opacity = '0.4';
    }
}

function dragend_file(e) {
    for (var key in selected_file_list) {
        $("tr[data-key=\"" + selected_file_list[key] + "\"]")[0].style.opacity = '1';
    }
}

function drop_file(e) {
    e.preventDefault();
    if ($(e.target).closest("tr").attr("data-type") === 'folder') {
        move_file($(e.target).closest("tr").attr("data-key"), selected_file_list);
    }
}

function allowDrop_file(e) {
    e.preventDefault();
}
