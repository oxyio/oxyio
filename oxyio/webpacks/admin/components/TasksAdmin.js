// oxy.io
// File: oxyio/webpacks/admin/components/TasksAdmin.js
// Desc: task admin component

import React, { Component } from 'react';

import OxyWebSocket from 'base/js/websocket';


export default class TasksAdmin extends Component {
    constructor(props) {
        super(props)

        this.state = {
            activeTaskIds: [],
            newTaskIds: [],
            endTaskIds: [],
            tasks: {},
            // Highlighted/detail task
            taskId: null,
            taskMessages: []
        }
    }

    componentDidMount() {
        this.socket = OxyWebSocket(
            this.props.requestKey,
            this.handleEvent.bind(this)
        );
    }

    handleEvent(event, data) {
        const stateDiff = {};

        switch(event) {
            case 'active_tasks':
                stateDiff.activeTaskIds = data;
                break;

            case 'new_tasks':
                stateDiff.newTaskIds = data;
                break;

            case 'end_tasks':
                stateDiff.endTaskIds = data;
                break;

            case 'tasks':
                stateDiff.tasks = data;
                break;

            case 'task_message':
                stateDiff.taskMessages = [data].concat(this.state.taskMessages);
                break;

            default:
                console.log('Unhandled event!', event, data);
        }

        // Apply any changes
        this.setState(stateDiff);
    }

    showTask(taskId) {
        // Tell the websocket to send the new tasks messages
        this.socket.emit('subscribe_task_id', {
            task_id: taskId
        });

        // Set ID & reset messages
        this.setState({
            taskId: taskId,
            taskMessages: []
        });
    }

    getTaskList(taskIds) {
        const taskItems = taskIds.map((taskId) => {
            return (
                <li
                    key={taskId}
                    onClick={() => this.showTask(taskId)}
                >{taskId}</li>
            );
        });

        return (
            <ul>
                {taskItems}
            </ul>
        );
    }

    getTaskInfo() {
        if (!this.state.taskId)
            return 'Please select a task';

        const { taskId } = this.state;
        const task = this.state.tasks[taskId];

        return (
            <div>
                <h3>
                    Task: {taskId}<br />
                    {task.local == 'true' ? <small>local</small> : ''}
                </h3>

                <p>
                    Task: <strong>{task.task}</strong><br />
                    State: <strong>{task.state}</strong><br />
                    Updated: <strong>{task.last_update}</strong>
                </p>
            </div>
        );
    }

    getTaskMessages() {
        const messages = this.state.taskMessages.map((message) => {
            message = JSON.parse(message);
            message = JSON.stringify(message, null, 2);
            return message;
        });

        return (
            <div className='task-messages'>
                <h3>Task Events</h3>
                <pre><code>
                    {messages}
                </code></pre>
            </div>
        );
    }

    render() {
        return (
            <div className='block base'>
                <div className='block third'>
                    <h3>Active Tasks</h3>
                    {this.getTaskList(this.state.activeTaskIds)}

                    <div className='block base'>
                        <div className='block half'>
                            <h3>New Tasks</h3>
                            {this.getTaskList(this.state.newTaskIds)}
                        </div>

                        <div className='block half'>
                            <h3>Ended Tasks</h3>
                            {this.getTaskList(this.state.endTaskIds)}
                        </div>
                    </div>
                </div>

                <div className='block two-third'>
                    {this.getTaskInfo()}
                    {this.getTaskMessages()}
                </div>
            </div>
        );
    }
}
