

---

### API文档

---

#### 1. 任务(Task) API

**1.1 获取团队所有任务**

- **URL**: `/api/teams/<team_id>/tasks/`
- **方法**: `GET`
- **权限**: `IsAuthenticated`
- **URL参数**:
  - `team_id`: 团队ID

**1.2 创建新任务**

- **URL**: `/api/teams/<team_id>/tasks/`
- **方法**: `POST`
- **权限**: `IsAuthenticated`
- **请求体**:
  ```json
  {
    "title": "任务标题",
    "description": "任务描述",
    
  }
  ```



---

#### 2. 页面(Page) API

**2.1 获取任务下所有页面**

- **URL**: `/api/teams/<team_id>/tasks/<task_id>/pages/`

- **方法**: `GET`

- **权限**: `IsAuthenticated`

- **URL参数**:
  - `team_id`: 团队ID
  - `task_id`: 任务ID
  
- 返回

  ```
  [
      {
          "id": 1,
          "name": "页面名称",
          "background_color": "#FFFFFF",
          "image": null,
          "width": 120,
          "height": 80,
          "created_date": "2023-08-27T15:31:01.700568+08:00",
          "last_modified": "2023-08-27T15:31:01.700568+08:00",
          "task": 3
      }
  ]
  ```

  

**2.2 创建新页面**

- **URL**: `/api/teams/<team_id>/tasks/<task_id>/pages/`
- **方法**: `POST`
- **权限**: `IsAuthenticated`
- **请求体**:
  ```json
  {
    "name": "页面名称",
    "background_color": "#FFFFFF",
    "width":120,
    "height":80 ,
     
  }
  ```





**更新页面API**

### **URL**:

`/api/teams/<team_id>/tasks/<task_id>/pages/<page_id>/`

### **方法**: 
`PUT`

### **权限**: 
- `IsAuthenticated`

### **URL参数**: 
- `team_id`: 团队的ID
- `task_id`: 任务的ID
- `page_id`: 页面的ID

### **请求体**:
```json
{
  "name": "新页面名称",
  "background_color": "#FFAABB",
  "width": 500,
  "height": 300
}
```

**字段说明**:
- `name` (string): 页面的名称
- `background_color` (string): 页面的背景颜色，格式为`#RRGGBB`
- `width` (integer): 页面的宽度
- `height` (integer): 页面的高度

### **成功响应**:
**Code**: `200 OK`

**Content**:
```json
{
  "id": 5,
  "name": "新页面名称",
  "background_color": "#FFAABB",
  "width": 500,
  "height": 300,
  "task": 3,
  "created_date": "2023-08-27T10:00:00Z",
  "last_modified": "2023-08-27T10:10:00Z"
}
```

### **错误响应**:
- **Code**: `400 BAD REQUEST`

  **Content**: 
  ```json
  {
    "name": ["This field is required."],
    "background_color": ["This field is required."],
    "width": ["This field is required."],
    "height": ["This field is required."]
  }
  ```

- **Code**: `404 NOT FOUND`

  **Content**: 
  ```json
  {
    "detail": "Page not found."
  }
  ```



---

#### 3. 组件(Component) API

**3.1 获取页面下所有组件**

- **URL**: `/api/teams/<team_id>/tasks/<task_id>/pages/<page_id>/components/`

- **方法**: `GET`

- **权限**: `IsAuthenticated`

- 返回

  ```
  [
      {
          "id": 1,
          "component_type": "button",
          "name": "组件名称",
          "x_position": 12,
          "y_position": 23,
          "width": 12,
          "height": 23,
          "page": 1
      }
  ]
  ```

  

**3.2 创建新组件**

- **URL**: `/api/teams/<team_id>/tasks/<task_id>/pages/<page_id>/components/`
- **方法**: `POST`
- **权限**: `IsAuthenticated`
- **请求体**:
  ```json
  {
    "component_type": "button",
    "name": "组件名称",
     "x_position" :12,
     "y_position" :23,
     "width" : 12,
     "height" : 23
  }
  ```

**3.3 更新组件**

- **URL**: `/api/teams/<team_id>/tasks/<task_id>/pages/<page_id>/components/<component_id>/`
- **方法**: `PUT` 或 `PATCH`
- **权限**: `IsAuthenticated`
- **请求体**:
  ```json
  {
    "component_type": "button",
    "name": "组件名称",
     "x_position" :12,
     "y_position" :23,
     "width" : 12,
     "height" : 23
  }
  ```

**3.4 删除组件**

- **URL**: `/api/teams/<team_id>/tasks/<task_id>/pages/<page_id>/components/<component_id>/`
- **方法**: `DELETE`
- **权限**: `IsAuthenticated`

