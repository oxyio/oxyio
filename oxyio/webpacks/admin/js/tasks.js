// oxy.io
// File: oxyio/webpacks/admin/js/tasks.js
// Desc: mounts the task status on the [data-tasks] element

import React from 'react';
import ReactDOM from 'react-dom';

import TasksAdmin from 'admin/components/TasksAdmin';


window.addEventListener('load', () => {
    const $tasksAdmin = document.querySelector('[data-tasks]');

    if ($tasksAdmin) {
        const requestKey = $tasksAdmin.getAttribute('data-tasks');

        ReactDOM.render(
            <TasksAdmin requestKey={requestKey} />,
            $tasksAdmin
        );
    }
});
