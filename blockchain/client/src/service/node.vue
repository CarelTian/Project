<template>
<div classs="content">
  <el-card shadow="hover">
    <el-row class="rowSpace">
        <el-col :span="4">
          <el-button
            type="primary"
            size="small"
            @click="add()"
            >新增节点</el-button
          ></el-col
        >
        <el-col :span="8">
        </el-col>
    </el-row>
    <el-table ref="Ninfo":data="tableData" stripe border>
      <el-table-column type="index" label="序号" width="50"/>
      <el-table-column prop="nodename" label="节点名称" />
      <el-table-column prop="ip" label="IP地址" />
      <el-table-column prop="publickey" label="公钥" />
       <el-table-column prop="option" align="center" label="操作" width="300">
         <template slot-scope="scope">
            <el-button
              type="primary"
              size="small"
              >编辑</el-button
            >
            <el-button
              type="danger"
              size="small"
              @click="dele(scope.row.ip)"
              >删除</el-button
            >
          </template>
       </el-table-column>
    </el-table>
  </el-card>
  <el-dialog
  title="添加节点"
  :visible.sync="dialog"
  width="30%"
  :before-close="CloseAddNode">
    <el-form
      ref="addnode"
      :rules="rules"
      :model="addnode"
      label-width="90px">
      <el-form-item label="节点名称:" prop="nodename">
        <el-input
          v-model="addnode.nodename"
          placeholder="请输入节点名称"/>
      </el-form-item>
      <el-form-item label="IP地址:" prop="ip">
        <el-input
          v-model="addnode.ip"
          placeholder="请输入节点IP"/>
      </el-form-item>
      <el-form-item label="公钥:" prop="publickey">
        <el-upload
          action="http://127.0.0.1:8000/api/addnode"
          :limit="1"
          ref="upload"
          :http-request="httpRequest"
          :auto-upload="false">
        <el-button size="small" icon="el-icon-upload">点击上传</el-button>
      </el-upload>
      </el-form-item>
      <el-form-item>
        <el-button size="small" @click="CloseAddNode()">取 消</el-button>
        <el-button size="small" type="primary" @click="SubmitNode()">提 交</el-button>
      </el-form-item>
    </el-form>
</el-dialog>

</div>
</template>

<script>
import axios from "axios";
export default {
  data() {
    return {
      dialog: false,
      tableData: [{
        nodename: 'N0',
        ip: "127.0.0.7",
        publickey: "./Keys/N0"
      }],
      addnode: {
        nodename: "",
        ip: "",
        publickey: ""
      },
      rules: {
        nodename: {
          required: true,
          message: "请输入节点名称",
          trigger: "blur",
        },
        ip: {
          required: true,
          message: "请输入节点IP",
          trigger: "blur",
        },
      },
      file:''

    };
  },
  created() {

  },
  methods: {
    CloseAddNode() {
      this.dialog = false;
      this.$refs.addnode.resetFields();
    },
    add() {
      this.dialog = true;
    },
    httpRequest(param){
      let file=param.file;
      this.file=file;
    },
    dele(name){
      let index=null;
      index=this.tableData.findIndex(item=>{
        if(item.name==name) return true
      })
      this.tableData.splice(index,1);
    },

    SubmitNode() {
      this.$refs.addnode.validate(async (valid) => {
        if (!valid) return;
        this.$refs.upload.submit();
        let fd=new FormData();
        fd.append('file',this.file);
        fd.append('nodename',this.addnode.nodename);
        fd.append('ip',this.addnode.ip);
        let config={
        headers:{
          'Content-Type':'multipart/form-data;boundary=----WebKitFormBoundarynl6gT1BKdPWIejNq',
        }
      };
            this.$axios
            .post("/api/addnode", fd,config)
            .then((res) => {
              if (res.data.success) {
                console.log(fd.get('nodename'));
                this.$message.success("保存成功！");
                let dir='./Keys/'+fd.get('file').name;
                this.tableData.push({nodename:fd.get('nodename'),ip:fd.get('ip'),publickey:dir});
              } else {
                this.$message.error(res.data.msg);
              }
            })
            .catch((err) => {
              console.log(err)
              this.$message.error("服务器连接失败");
              this.loginLoading = false;
            });

        this.CloseAddNode();
      });
    },

  }
}



</script>

<style scoped>
.el-table {
  margin: 20px 0px;
}
</style>
