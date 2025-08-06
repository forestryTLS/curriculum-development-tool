var draggables = document.querySelectorAll('.draggable')
var containers = document.querySelectorAll('.drag_container')

draggables.forEach(draggable => {
    draggable.addEventListener('dragstart', () => {
        draggable.classList.add('dragging')
    })

    draggable.addEventListener('dragend', () => {
        draggable.classList.remove('dragging')
    })
})

containers.forEach(container => {
    container.addEventListener('dragover' , e => {
        e.preventDefault()
        var afterElement = getDragAfterElement(container, e.clientY)
        var draggable = document.querySelector(".dragging")
        if( afterElement == null){
            container.appendChild(draggable)
        }else{
            container.insertBefore(draggable,afterElement)
        }
    })
})

function getDragAfterElement(container, y) {
    var draggableElements = [...container.querySelectorAll('.draggable:not(.dragging')]

 return draggableElements.reduce(( closest, child ) => {
        var box = child.getBoundingClientRect()
        var offset = y - box.top - box.height / 2
        if (offset < 0 && offset > closest.offset){
            return { offset:offset, element: child}
        }else{
            return closest
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element
}
