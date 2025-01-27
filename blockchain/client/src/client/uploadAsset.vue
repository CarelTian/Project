<template>
<div classs="content">
  <el-card shadow="hover">
    <el-row class="rowSpace">
        <el-col :span="4">
          <el-button
            type="primary"
            size="small"
            @click="add()"
            >上传虚拟财产</el-button
          ></el-col
        >
        <el-col :span="8">
        </el-col>
    </el-row>
    <el-table ref="Ninfo":data="tableData" stripe border>
      <el-table-column type="index" label="序号" width="50"/>
      <el-table-column prop="address" label="地址" width="300" />
      <el-table-column prop="type" label="财产类型" />
      <el-table-column prop="asset" label="财产名称" />
      <el-table-column prop="node" label="认证节点" />
      <el-table-column prop="state" label="状态">
      </el-table-column>
    </el-table>
  </el-card>
  <el-dialog
  title="上传虚拟财产"
  :visible.sync="dialog"
  width="30%"
  :before-close="CloseAdd">
    <el-form
      ref="addasset"
      :rules="rules"
      :model="addasset"
      label-width="90px">
      <el-form-item label="地址:" prop="address">
        <el-input
          v-model="addasset.address"
          placeholder="请输入区块链地址"/>
      </el-form-item>
      <el-form-item label="类型:" prop="type">
        <el-input
          v-model="addasset.type"
          placeholder="请输入类型"/>
      </el-form-item>
      <el-form-item label="名称: " prop="asset">
        <el-input
          v-model="addasset.asset"
          placeholder="请输入类型"/>
      </el-form-item>
      <el-form-item label="文件:" prop="file">
        <el-upload
          :limit="1"
          ref="upload"
          :before-upload="beforeunload"
          :http-request="httpRequest"
          :auto-upload="false">
        <el-button size="small" icon="el-icon-upload">点击上传</el-button>
      </el-upload>
      </el-form-item>
      <el-form-item>
        <el-button size="small" @click="CloseAdd()">取 消</el-button>
        <el-button size="small" type="primary" @click="SubmitAsset()">提 交</el-button>
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
        address:'',
        type:'',
        asset:'',
        node:'',
        state:''

      }],
      addasset: {
        address: "",
        type: "",
        asset: ""
      },
      rules: {
        address: {
          required: true,
          message: "请输入地址",
          trigger: "blur",
        },
        type: {
          required: true,
          message: "请输入虚拟财产类型",
          trigger: "blur",
        },
        asset: {
          required: true,
          message: "请输入虚拟财产名称",
          trigger: "blur",
        },
      },
      file:'',
      check:true

    };
  },
  created() {
      this.GetTable();
  },
  methods: {
    CloseAdd() {
      this.dialog = false;
      this.$refs.addasset.resetFields();
      this.$refs.upload.clearFiles()
    },
    add() {
      this.dialog = true;
    },
    httpRequest(param){
      let file=param.file;
      this.file=file;
    },
    async GetTable(){
      const result = await this.$axios.get("/api/myupload");
      if (result.data.success) {
        this.tableData=result.data.data;
      } else {
        this.$message.error(result.data.msg);
      }

    },

    SubmitAsset() {
      this.$refs.addasset.validate(async (valid) => {
        if (!valid) return;
        this.$refs.upload.submit();
        if (!this.check) return;
        let fd=new FormData();
        fd.append('file',this.file);
        fd.append('address',this.addasset.address);
        fd.append('type',this.addasset.type);
        fd.append('asset',this.addasset.asset);
        let config={
        headers:{
          'Content-Type':'multipart/form-data;boundary=----WebKitFormBoundarynl6gT1BKdPWIejNq',
        }
      };
            this.$axios
            .post("/api/upload", fd,config)
            .then((res) => {
              if (res.data.success) {
                this.$message.success("保存成功！");
                this.tableData.push({address:fd.get('address'),type:fd.get('type'),asset:fd.get('asset'),
                 node:'N0',state:'未审核'});
              } else {
                this.$message.error(res.data.msg);
              }
            })
            .catch((err) => {
              console.log(err)
              this.$message.error("服务器连接失败");
              this.loginLoading = false;
            });

        this.CloseAdd();
      });
    },
    beforeunload(file){
      var suffix= file.name.substring(file.name.lastIndexOf('.') + 1)
      var type=this.addasset.type
      if(type=="图片"&&(suffix!='png'&&suffix!='jpg'&&suffix!='jpeg')){
        this.check=false;
        this.$message.error("图片形式只支持png,jpg,jpeg格式");
        return false;
      }
      return true;
    }

  }
}



</script>

<style scoped>
.el-table {
  margin: 20px 0px;
}
</style>
